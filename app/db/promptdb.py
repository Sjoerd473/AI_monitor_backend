from psycopg.rows import dict_row

# PromptDB is a class so we can encapsulate all the database logic in one place
# This gives a cleaner API, centralized connection management, separation of concerns
# and also easier testing/mocking, if we actually did any...
# thus no need to repeat boilerplate code

class PromptDB:
    def __init__(self, pool):
        self.pool = pool

        # These are all variables we use in methods inside this class
        self.INSERT_QUERIES = {
            "users": "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
            "models": "INSERT INTO models (model_name, model_mode) VALUES (%s, %s) ON CONFLICT (model_name, model_mode) DO NOTHING",
            "sessions": "INSERT INTO sessions (session_id, user_id, session_start, session_prompt_count, session_duration) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (session_id) DO UPDATE SET session_prompt_count = EXCLUDED.session_prompt_count, session_duration = EXCLUDED.session_duration",
            "prompts": "INSERT INTO prompts (user_id, session_id, model_id, conversation_id, characters_in, tokens_in, timestamp, domain, type, language, source, energy_consumption_wh, co2_output_g, water_consumption_l) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING prompt_id",
            "responses": "INSERT INTO responses (prompt_id, character_out, latency, streaming_duration) VALUES (%s, %s, %s, %s)",
            "environment": "INSERT INTO environment (prompt_id, browser, version, os, viewport, timezone, region, plugin_version) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            "ui": "INSERT INTO ui_interactions (prompt_id, regenerate_used, suggested_prompt_used, image_attached, file_attached, voice_input, tool_active) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            "conversations": "INSERT INTO conversations (conversation_id) VALUES (%s) ON CONFLICT (conversation_id) DO NOTHING",
        }

        self.METRICS = {
            "co2": "co2_output_g",
            "water": "water_consumption_l",
            "energy": "energy_consumption_wh",
        }

        self.DIMENSIONS = {
            "category": {
                "col": "domain",
                "join": "",
                "table": "p"
            },
            "model": {
                "col": "model_name",
                "join": "LEFT JOIN models ON models.model_id = p.model_id",
                "table": "models"
            }
        }

        self.TIME_CONFIG = {
        
            "hour": {
                "format": "HH24:MI",
                "previous": (
                    "date_trunc('day', CURRENT_DATE - INTERVAL '1 day')",
                    "date_trunc('day', CURRENT_DATE - INTERVAL '1 day') + INTERVAL '23 hours'",
                    "INTERVAL '1 hour'"
                ),
                "current": (
                    "date_trunc('day', NOW())",
                    "date_trunc('hour', NOW())",
                    "INTERVAL '1 hour'"
                )
            },

            "day": {
                "format": "Dy",
                "previous": (
                    "date_trunc('week', CURRENT_DATE) - INTERVAL '1 week'",
                    "date_trunc('week', CURRENT_DATE) - INTERVAL '1 day'",
                    "INTERVAL '1 day'"
                ),
                "current": (
                    "date_trunc('week', CURRENT_DATE)",
                    "CURRENT_DATE",
                    "INTERVAL '1 day'"
                )
            },

            "week": {
                "format": "DD Mon",
                "previous": (
                    "date_trunc('month', CURRENT_DATE) - INTERVAL '1 month'",
                    "date_trunc('month', CURRENT_DATE) - INTERVAL '1 week'",
                    "INTERVAL '1 week'"
                ),
                "current": (
                    "date_trunc('month', CURRENT_DATE)",
                    "date_trunc('week', CURRENT_DATE)",
                    "INTERVAL '1 week'"
                )
            }
        }
    # this keeps everything more DRY
 
    # def _execute(self, query, params=None, *, fetch=False, many=False):
    
    #     with self.pool.connection() as conn:
    #         try:
    #             with conn.cursor(row_factory=dict_row) as cur:
    #                 if many:
    #                     cur.executemany(query, params)
    #                 else:
    #                     cur.execute(query, params)

    #                 if fetch:
    #                     return cur.fetchall()
    #                

    #             conn.commit()

    #         except Exception:
    #             conn.rollback()
    #             raise
           
            # the Exception bubbles up instead, to be handles higher up in the chain (and is not modified here)
    # the _ at the start of a method indicates that these are private methods, that should not be called outside of the class
    #     # * makes the following arguments keyword only (so _execute(... False ...) won't work)
    def _execute(self, query, params=None, *, fetch=False, many=False, conn=None):
        # If a connection is provided, we use it directly without managing lifecycle
        if conn:
     # open a cursor to perform database interactions
            with conn.cursor(row_factory=dict_row) as cur:
                 # execute a command based on the parameters passed into the method
                if many:
                    cur.executemany(query, params)
                else:
                    cur.execute(query, params)
                return cur.fetchall() if fetch else None
            # This commits inside the methods that runs with its own connection

        # Otherwise, we manage the connection from the pool (standard behavior)
        with self.pool.connection() as new_conn:
            try:
                with new_conn.cursor(row_factory=dict_row) as cur:
                    if many:
                        cur.executemany(query, params)
                    else:
                        cur.execute(query, params)
                    result = cur.fetchall() if fetch else None
                # commit the changes to the DB, otherwise nothing is saved.
                new_conn.commit()
                return result
            except Exception:
            # without the rollback the connection would be left in a failed transaction state,
            #  leaving said connection unusable > all commands fail
            # rollback undoes all changes made in the current transaction, then returns the connection to the pool
                new_conn.rollback()
                raise

    # wrappers
    # these pretty much do what you'd expect, read for reading, write/write_many for writing one or for writing many at once.
    def _read(self, query, params=None, conn=None):
        return self._execute(query, params, fetch=True, conn=conn)

    def _write(self, query, params=None, conn=None):
        self._execute(query, params, conn=conn)

    def _write_many(self, query, seq_of_params, conn=None):
        self._execute(query, seq_of_params, many=True, conn=conn)

    # we only use this to get the IDs generated at moment of writing 
    def _write_many_returning(self, query, seq_of_params, conn=None):
        returned_ids = []

        # If we have a shared connection, we loop using its cursor
        if conn:
            with conn.cursor(row_factory=dict_row) as cur:
                for params in seq_of_params:
                    cur.execute(query, params)
                    result = cur.fetchone()
                    if not result:
                        returned_ids.append(None)
                        continue
                    first_column_name = list(result.keys())[0]
                    returned_ids.append(result[first_column_name])
            return returned_ids

        # Fallback: If no conn is passed, we open a new one for the whole loop
        with self.pool.connection() as new_conn:
            ids = self._write_many_returning(query, seq_of_params, conn=new_conn)
            new_conn.commit()
            return ids

    
    
    # this method helps build the retrieval query.
    # Metric is co2/water/energy
    # Time_unit is day/week/month
    # period is previous/current
    def _chart_sql(self, metric, time_unit, period, dimension=None):
        # we pull the config from the time_unit passed into the method
        cfg = self.TIME_CONFIG[time_unit]
        # cfg[period] is a tuple with three strings, that corrispond to the start,
        # end, and interval of the query
        start, end, interval = cfg[period]
        # each time_unit also has a specific format
        label_fmt = cfg["format"]
        # the required metric is assigned to column as the column to extract from the DB
        column = self.METRICS[metric]
        # and the key is composed out of these three parameters, which can become 'water_day_current' etc.
        key = f"{metric}_{time_unit}_{period}"

        # these are instantiated here to ensure they are declared in all control-flow branches
        # and so their default is 'no extra SQL', not None 
        dim_join = ""
        where_clause = ""

        # this is True when we are pulling categories and models
        if dimension:
            # it gets the category or model object from DIMENSIONS
            # and then configures each variable with the right data from said object
            dim_cfg = self.DIMENSIONS[dimension]
            col = dim_cfg["col"]
            table = dim_cfg["table"]
            dim_join   = dim_cfg["join"] or ""
            where_clause = f"WHERE {table}.{col} = p_outer.{col}"
            # and then composes the correct SQL query
       
        join_clause = f"""
                LEFT JOIN prompts p 
                    ON p.timestamp >= g.bucket 
                    AND p.timestamp < g.bucket + {interval}
                {dim_join}
            """
      

        return f"""
            '{key}',
            (
                SELECT json_build_object(
                    'labels', json_agg(to_char(bucket, '{label_fmt}') ORDER BY bucket),
                    'data',   json_agg(value ORDER BY bucket)
                )
                FROM (
                    SELECT
                        g.bucket,
                        COALESCE(SUM(p.{column}), 0) AS value
                    FROM generate_series({start}, {end}, {interval}) g(bucket)
                    {join_clause}
                    {where_clause}  -- Apply filtering here
                    GROUP BY g.bucket
                    ORDER BY g.bucket
                ) s
            )
        """
    # This loops over the three properties to compose an SQL query that pulls
    # the desired temporal data from the DB
    def _build_global_query(self):
        
        blocks = []

        for metric in self.METRICS:
            for time_unit in self.TIME_CONFIG:
                for period in ("previous","current"):

                    blocks.append(
                        self._chart_sql(metric, time_unit, period)
                    )
        # every string inside blocks is inserted into the return string, seperated by a comma
        return f"""
        SELECT json_build_object(
            {",".join(blocks)}
        ) AS dashboard
        """
    # the queries for category and model need a different query
    def _build_dimension_query(self, dimension):
        dim_cfg = self.DIMENSIONS[dimension]
        dim_col = dim_cfg["col"]
        # dim_join needs to not be None, even if it is not needed
        # the 'or' will only be True if it is not present in the dim_cfg object
        dim_join = dim_cfg["join"] or ""

        # Use the correct table alias for the distinct column
        # For "model", model_name comes from the joined "models" table, not "p"
       
        distinct_table = dim_cfg["table"]
        # here too we create an array with query strings
        blocks = []
        for metric in self.METRICS:
            for time_unit in self.TIME_CONFIG:
                for period in ("previous", "current"):
                    blocks.append(self._chart_sql(metric, time_unit, period, dimension))

        # and then return the whole constructed query.
        return f"""
        SELECT json_object_agg(
            p_outer.{dim_col},
            json_build_object(
                {",".join(blocks)}
            )
        ) AS dashboard
        FROM (
            SELECT DISTINCT {distinct_table}.{dim_col}
            FROM prompts p
            {dim_join}
        ) p_outer
        """
    # this gets all the generic prompt data
    def get_dashboard_global(self):

        query = self._build_global_query()
        result = self._read(query)
        # the returned result is a list of dicts, even if there is only one row
        # so [0] grabs the first (and only) row, and then the column 'dashboard'
        # which is the big .json object
        return result[0]["dashboard"] # type: ignore

    # This gets all the category or model data
    def get_dashboard_by_column(self, column):
        query = self._build_dimension_query(column)
        result = self._read(query)
        return result[0]["dashboard"] # type: ignore
    

    # this has Conn because it is called twice in insert_prompts
    def get_models(self, conn=None):
        return self._read("SELECT model_id, model_name, model_mode FROM models", conn=conn)
    
    # obsolete
    def get_all_data(self):

        query = """SELECT json_build_object(
          'schema_version', '1.0',
          'exported_at', NOW(),
          'users', (SELECT json_agg(row_to_json(u)) FROM users u),
          'models', (SELECT json_agg(row_to_json(m)) FROM models m),
          'sessions', (SELECT json_agg(row_to_json(s)) FROM sessions s),
          'prompts', (SELECT json_agg(row_to_json(p)) FROM prompts p),
          'responses', (SELECT json_agg(row_to_json(r)) FROM responses r),
          'environment', (SELECT json_agg(row_to_json(e)) FROM environment e),
          'ui_interactions', (SELECT json_agg(row_to_json(ui)) FROM ui_interactions ui),
          'conversations', (SELECT json_agg(row_to_json(c)) FROM conversations c)
        ) AS db_json;"""

        return self._read(query)


    def get_token(self, token_hash):
        query = "SELECT user_id FROM api_tokens WHERE token_hash = %s"
        result = self._read(query, (token_hash,))
        # returns a dict with one key-value pair
        return result[0] if result else None

    def update_token_last_used(self, token_hash):
        query = "UPDATE api_tokens SET last_used = now() WHERE token_hash = %s"
        self._write(query, (token_hash,))

 
    def insert_token(self,user_id, token_hash):

        query = """
             INSERT INTO api_tokens (user_id, token_hash)
             VALUES (%s, %s)
             ON CONFLICT (user_id) DO UPDATE SET
                 token_hash = EXCLUDED.token_hash,
                 created_at = now()
        """
        return self._write(query, (user_id, token_hash))
    
    def insert_user(self, user_id):
        query = self.INSERT_QUERIES["users"]
        self._write(query, (user_id,))
    
    # def log_download(self, user_id):
    #     query = "INSERT INTO download_log (user_id) VALUES (%s)"
    #     self._write(query, (user_id,))

    # def get_last_download(self, user_id):
    #     query = """
    #         SELECT downloaded_at FROM download_log
    #         WHERE user_id = %s
    #         ORDER BY downloaded_at DESC
    #         LIMIT 1
    #     """
    #     result = self._read(query, (user_id,))
    #     return result[0] if result else None

    
            
    def insert_prompts(self, batch):
        # this opens its own private conn(ecction), so we open one, and only one,
        # for the entire insert statement, by passing it into every method that we call.
        with self.pool.connection() as conn:
            try:
                # --- Step 0: Prepare model lookup ---
                # queries the database for all existing models
                # and turns it into a map for quicker lookups
                existing_models = {
                    (m["model_name"], m["model_mode"]): m["model_id"]
                    for m in self.get_models(conn=conn) # type: ignore
                }

                # Identify new models not yet in DB
                # A set can't have duplicate values, so all the models in there are unique
                # if a model coming in from a prompt is not in the dict, it adds it to it
                new_models = set()
                for b in batch:
                    model = b["model"]
                    key = (model["model_name"], model["model_mode"])
                    if key not in existing_models:
                        new_models.add(key)

                # Insert missing models
                # if there is infact a new model, it gets added to the database, and then to existing_models
                if new_models:
                    self._write_many(self.INSERT_QUERIES["models"], [tuple(m) for m in new_models], conn=conn)
                    # Update mapping using the same connection
                    existing_models.update({
                        (m["model_name"], m["model_mode"]): m["model_id"]
                        for m in self.get_models(conn=conn) # type: ignore
                    })

                # --- Step 1: Build parent rows ---
                # all inserts must be done with tuples, so there is a lot of converting going on
                # grabs all user_ids out of the batch and puts them as tuples in a list
                users_rows = [(b["user"]["user_id"],) for b in batch]
                # grabs all session data out of the batch and puts it as tuples in a list
                sessions_rows = [
                    (
                        b["session"]["session_id"],
                        b["user"]["user_id"],
                        b["session"]["session_start"],
                        b["session"]["session_prompt_count"],
                        b["session"]["session_duration_ms"]
                    )
                    for b in batch
                ]

                conversations_rows = [(b["conversation_id"], ) for b in batch]

                # Insert parent tables
                # first two writes
                # they go first as they don't depend on anything
                self._write_many(self.INSERT_QUERIES["users"], users_rows, conn=conn)
                self._write_many(self.INSERT_QUERIES["sessions"], sessions_rows, conn=conn)
                self._write_many(self.INSERT_QUERIES["conversations"], conversations_rows, conn=conn)

                # --- Step 2: Build prompts ---
                # we create an empty list to keep the code easier to read
                prompts_rows = []
                for b in batch:
                    # we create these variables to avoid repeating them over and over again
                    user = b["user"]
                    session = b["session"]
                    model = b["model"]
                    prompt = b["prompt"]
                    # we look up the model id from the lookup dict, using the model name and mode
                    model_id = existing_models[(model["model_name"], model["model_mode"])]
                    # then we append all the prompt data as tuples to the list
                    prompts_rows.append((
                        user["user_id"],
                        session["session_id"],
                        model_id,
                        b["conversation_id"],
                        prompt["text_length"],
                        prompt["tokens_in"],
                        prompt["timestamp"],
                        prompt["domain"],
                        prompt["prompt_type"],
                        prompt["language"],
                        b["source"],
                        prompt["energy_wh"],
                        prompt["co2_g"],
                        prompt["water_l"]
                    ))

                # Bulk insert prompts and get their IDs
                # This is crucial, as the IDs are needed to correctly insert responses, env, and ui
                prompt_ids = self._write_many_returning(self.INSERT_QUERIES["prompts"], prompts_rows, conn=conn)

                # --- Step 3: Build child rows ---
                responses_rows = []
                env_rows = []
                ui_rows = []

                # we need to enumerate here, so we can simultaneously loop over the list of prompt_ids
                for i, b in enumerate(batch):
                    # also here we create some variables to avoid repetition
                    pid = prompt_ids[i]
                    response = b["response"]
                    env = b["environment"]
                    ui = b["ui_interaction"]

                    # and then create append all the data as tuples to their lists
                    responses_rows.append((
                        pid,
                        response["characters_out"],
                        response["latency_ms"],
                        response["streaming_duration_ms"]
                    ))

                    env_rows.append((
                        pid,
                        env["browser"],
                        env["version"],
                        env["os"],
                        env["viewport"],
                        env["timezone"],
                        env["region"],
                        env["plugin_version"]
                    ))

                    ui_rows.append((
                        pid,
                        ui["regenerate_used"],
                        ui["suggested_prompt_used"],
                        ui["image_attached"],
                        ui["file_attached"],
                        ui["voice_input"],
                        ui["tool_active"]
                    ))

                # --- Step 4: Bulk insert child tables ---
                # then send it all into the DB
                self._write_many(self.INSERT_QUERIES["responses"], responses_rows, conn=conn)
                self._write_many(self.INSERT_QUERIES["environment"], env_rows, conn=conn)
                self._write_many(self.INSERT_QUERIES["ui"], ui_rows, conn=conn)

                conn.commit()

            except Exception:
                conn.rollback()
                raise
