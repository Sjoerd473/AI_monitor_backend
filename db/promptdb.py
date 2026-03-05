# - Connection.execute() → “Send this command to Postgres; I don’t need to read rows.”
# - Cursor.execute() → “Send this command and give me a handle to read the rows that come back.”

from db.pool import pool

class PromptDB:
    def __init__(self):
        self.pool = pool


# Private helpers #
    def _read(self, query, params=None):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
            
    def _write(self, query, params=None):
        with self.pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def _write_many(self, query, seq_of_params):
        with self.pool.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(query, seq_of_params)
                conn.commit()
            except Exception:
                conn.rollback()
                raise

# Public Methods #

    def insert_prompts(self, batch):
        query = """
    ...
    """
        self._write_many(query, batch)

    def get_users(self):
        return self._read("SELECT * FROM users")
  

