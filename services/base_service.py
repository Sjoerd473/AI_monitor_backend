from db.promptdb import PromptDB
from db.pool import pool

class BaseService:
    def __init__(self):
        self.db = PromptDB(pool)