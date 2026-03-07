# this is the class that reads from the DB
# all the SQL is abstracted away in promptdb.py

from services.base_service import BaseService, db_logging

class Retrieval(BaseService):
    # all these methods will call methods inside promptdb
    # this is the syntax for a decorator
    # equal to get_users = db_logging(get_users), but more elegant
    @db_logging
    def get_users(self):
        return self.db.get_users() ## all these functions should be called in a try except block, to handle the original error
    
   

# this is just for testing, to be deleted
if __name__ == "__main__":
    r = Retrieval()
