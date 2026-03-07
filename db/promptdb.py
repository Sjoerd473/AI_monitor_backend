# - Connection.execute() → “Send this command to Postgres; I don’t need to read rows.”
# - Cursor.execute() → “Send this command and give me a handle to read the rows that come back.”

# we import our connection pool here
from db.pool import pool

# PromptDB is a class so we can encapsulate all the database logic in one place
# This gives a cleaner API, centralized connection management, separation of concerns
# and also easier testing/mocking, if we actually did any...
# thus no need to repeat boilerplate code
# and no need for a global pool object (bad design)
class PromptDB:
    def __init__(self, pool):
        self.pool = pool
        self.INSERT_QUERIES = {
            "users": "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            "models": "INSERT INTO models (model_name, model_mode) VALUES (%s, %s) ON CONFLICT (model_name, model_mode) DO NOTHING",
            "sessions": "INSERT INTO sessions (session_id, session_start, session_prompt_count, session_duration) VALUES (%s, %s, %s, %s) ON CONFLICT (session_id) DO UPDATE SET session_prompt_count = EXCLUDED.session_prompt_count, session_duration = EXCLUDED.session_duration",
            "prompts": "INSERT INTO prompts (user_id, session_id, model_id, characters_in, tokens_in, timestamp, domain, type, safety_cat, language, source, energy_consumption, co2_output, water_consumption) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING prompt_id",
            "responses": "INSERT INTO responses (prompt_id, character_out, latency, streaming_duration) VALUES (%s, %s, %s, %s)",
            "environment": "INSERT INTO environment (prompt_id, browser, version, os, viewport, timezone, plugin_version) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            "ui": "INSERT INTO ui_interactions (prompt_id, regenerate_used, suggested_prompt_used, image_attached, file_attached, voice_input, tool_active) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        }
    # this keeps everything more DRY
    # the _ at the start of a method indicates that these are private methods, that should not be called outside of the class
    def _execute(self, query, params=None, *, fetch=False, many=False):
        # * makes the following arguments keyword only (so _execute(... False ...) won't work)
        with self.pool.connection() as conn:
            # open a connection
            try:
                with conn.cursor() as cur:
                    # open a cursor to perform database interactions
                    if many:
                        cur.executemany(query, params)
                    else:
                        cur.execute(query, params)

                    if fetch:
                        columns = [desc[0] for desc in cur.description]
                        return [dict(zip(columns, row)) for row in cur.fetchall()]
                    # execute a command based on the parameters passed into the method

                conn.commit()
                # commit the changes to the DB, otherwise nothing is saved.

            except Exception:
                conn.rollback()
                raise
            # without the rollback the connection would be left in a failed transaction state,
            #  leaving said connection unusable > all commands fail
            # rollback undoes all changes made in the current transaction, then returns the connection to the pool
            # the Exception bubbles up instead, to be handles higher up in the chain (and is not modified here)

    # wrappers
    # these pretty much do what you'd expect, read for reading, write/write_many for writing one or for writing many at once.
    def _read(self, query, params=None):
        return self._execute(query, params, fetch=True)

    def _write(self, query, params=None):
        self._execute(query, params)

    def _write_many(self, query, seq_of_params):
        self._execute(query, seq_of_params, many=True)

    def _write_many_returning(self, query, seq_of_params):
        returned_ids = []
        for params in seq_of_params:
            result = self._execute(query, params, fetch=True)
            if not result or len(result) == 0:
            # Row was not inserted (ON CONFLICT DO NOTHING)
                returned_ids.append(None)
                continue

            row = result[0]  # This is a dict
        # Get the first column's value (usually the returning id)
            returned_ids.append(next(iter(row.values())))
        return returned_ids

    
    def _get_timerange(self,time_unit, time_range, func):
        return f"""SELECT date_trunc('{time_unit}', timestamp) AS date, {func}
        FROM prompts
        GROUP BY 1
        ORDER BY 1
        LIMIT {time_range}"""

# Public Methods #
# this will be a list of all the queries we use, too messy?

        
  
    def get_users(self):
        return self._read("SELECT * FROM users")

    def get_prompts(self):
        return self._read("SELECT * FROM prompts")
    
    def get_CO2_by_day(self):
        return self._read(self._get_timerange("day",7,"SUM(co2_output)"))
    
    def get_models(self):
        return self._read("SELECT model_id, model_name, model_mode FROM models")
    
    
            
    def insert_prompts(self, batch):
            # --- Step 0: Prepare model lookup ---
            existing_models = { (m["model_name"], m["model_mode"]): m["model_id"] for m in self.get_models() }
            new_models = set((b["model"]["model_name"], b["model"]["model_mode"]) for b in batch if (b["model"]["model_name"], b["model"]["model_mode"]) not in existing_models)
            # Insert new models if missing
            if new_models:
                self._write_many(self.INSERT_QUERIES["models"], [tuple(m) for m in new_models])
                # Re-fetch models to update mapping
                existing_models.update({ (m["model_name"], m["model_mode"]): m["model_id"] for m in self.get_models() })

            # --- Step 1: Build parent rows ---
            users_rows = [ (b["user"]["user_id"],) for b in batch ]
            sessions_rows = [
                (
                    b["session"]["session_id"],
                    b["session"]["session_start"],
                    b["session"]["session_prompt_count"],
                    b["session"]["session_duration_ms"]
                ) for b in batch
            ]

            self._write_many(self.INSERT_QUERIES["users"], users_rows)
            self._write_many(self.INSERT_QUERIES["sessions"], sessions_rows)

            # --- Step 2: Build prompts and insert, capturing prompt_ids ---
            prompts_rows = []
            for b in batch:
                model_key = (b["model"]["model_name"], b["model"]["model_mode"])
                prompts_rows.append((
                    b["user"]["user_id"],
                    b["session"]["session_id"],
                    existing_models[model_key],
                    b["prompt"]["text_length"],
                    b["prompt"]["tokens_in"],
                    b["prompt"]["timestamp"],
                    b["prompt"]["domain"],
                    b["prompt"]["prompt_type"],
                    b["prompt"]["safety_category"],
                    b["prompt"]["language"],
                    b["source"],
                    b["prompt"]["energy_wh"],
                    b["prompt"]["co2_g"],
                    b["prompt"]["water_l"]
                ))

            # Bulk insert prompts with RETURNING prompt_id
            prompt_ids = self._write_many_returning(self.INSERT_QUERIES["prompts"], prompts_rows)
            # prompt_ids should be in the same order as batch

            # --- Step 3: Build child rows ---
            responses_rows = []
            env_rows = []
            ui_rows = []

            for i, b in enumerate(batch):
                pid = prompt_ids[i]

                responses_rows.append((
                    pid,
                    b["response"]["characters_out"],
                    b["response"]["latency_ms"],
                    b["response"]["streaming_duration_ms"]
                ))

                env_rows.append((
                    pid,
                    b["environment"]["browser"],
                    b["environment"]["version"],
                    b["environment"]["os"],
                    b["environment"]["viewport"],
                    b["environment"]["timezone"],
                    b["environment"]["plugin_version"]
                ))

                ui_rows.append((
                    pid,
                    b["ui_interaction"]["regenerate_used"],
                    b["ui_interaction"]["suggested_prompt_used"],
                    b["ui_interaction"]["image_attached"],
                    b["ui_interaction"]["file_attached"],
                    b["ui_interaction"]["voice_input"],
                    b["ui_interaction"]["tool_active"]
                ))

            # --- Step 4: Bulk insert child tables ---
            self._write_many(self.INSERT_QUERIES["responses"], responses_rows)
            self._write_many(self.INSERT_QUERIES["environment"], env_rows)
            self._write_many(self.INSERT_QUERIES["ui"], ui_rows)

        # --- Helper method to fetch all models ---
    

        # Example helper: bulk write returning inserted IDs
   



# date_trunc(interval, timestamp) cuts off the smaller time units of a timestamp so everything aligns to a clean boundary.


# This selects all the sessions per day/week/month/year, one row for each timeunit
#     SELECT date_trunc('month', session_start), count(*)
# FROM sessions
# GROUP BY 1
# ORDER BY 1
# LIMIT X > 7 for days, 4 for weeks, or whatever
# this only works if there is data for these dates, otherwise skips over

# SELECT date_trunc('day', timestamp), sum(co2_output)
# FROM prompts
# GROUP BY 1
# ORDER BY 1
# LIMIT 7