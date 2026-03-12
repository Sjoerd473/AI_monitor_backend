import os
from psycopg_pool import ConnectionPool
# ConnectionPool is an object for managing a set of connections, allowing their use in fuctions that need one
# Establishing new connections can be relatively long, a pool lets us keep connections open
# Given that we do a lot of communicating with the DB, a pool makes more sense.
pool = ConnectionPool("dbname=prompts user=postgres password=megablaat")

# password is missing in connectionpool

# from config import settings

# pool = ConnectionPool(settings.database_url, min_size=2, max_size=10, timeout=30, open=False)