from psycopg_pool import ConnectionPool

pool = ConnectionPool("dbname=prompts user=postgres")

# password is missing in connectionpool