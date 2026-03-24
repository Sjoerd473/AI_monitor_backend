from config import settings
from psycopg_pool import ConnectionPool

# ConnectionPool is an object for managing a set of connections, allowing their use in fuctions that need one
# Establishing new connections can be relatively long, a pool lets us keep connections open
# Given that we do a lot of communicating with the DB, a pool makes more sense.



pool = ConnectionPool(settings.database_url, min_size=2, max_size=10, timeout=30, open=False)