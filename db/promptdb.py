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
    # a single method that handles all DB interactions, varying based on parameters passed into it
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
                        return cur.fetchall()
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
    
    def _get_timerange(self,time_unit, time_range, func):
        return f"""SELECT date_trunc('{time_unit}', timestamp) AS date, {func}
        FROM prompts
        GROUP BY 1
        ORDER BY 1
        LIMIT {time_range}"""

# Public Methods #
# this will be a list of all the queries we use, too messy?
    def insert_prompts(self, batch):
        query = """
    ...
    """
        self._write_many(query, batch)

    def get_users(self):
        return self._read("SELECT * FROM users")

    def get_prompts(self):
        return self._read("SELECT * FROM prompts")
    
    def get_CO2_by_day(self):
        return self._read(self._get_timerange("day",7,"SUM(co2_output)"))
  


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