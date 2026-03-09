# this file exists to take away this bit of boilerplate code from ingestion and retrieval
# in case we ever want to split up the quering classes more, we will not have to repeat this code everywhere
# or in case something changes in how we interact with the DB
# keeping it DRY!


import logging
from db.promptdb import PromptDB
from db.pool import pool

# __name__ represents the module name
logger = logging.getLogger(__name__)
# this is not yet configured, so the logs go to STOUT == the terminal

# db_logging is needed because it is called once at decorating time
# instead wrapper runs every time the actual function is called
def db_logging(func):
    def wrapper(*args, **kwargs):
        try:
            # this is the original function call, with the same parameters
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error and include traceback because exc_info=True
            logger.error(f"DB operation {func.__name__} failed", exc_info=True)
            # Re-raise the exception so it propagates
            # don't reraise to avoid a double error showing (so return None)
            raise
    # this is always called
    return wrapper

class BaseService:
    def __init__(self):
        self.db = PromptDB(pool)

    