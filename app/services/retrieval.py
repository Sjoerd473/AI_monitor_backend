# this is the class that reads from the DB
# all the SQL is abstracted away in promptdb.py

from services.base_service import BaseService, db_logging

class Retrieval(BaseService):
    # all these methods will call methods inside promptdb
    # this is the syntax for a decorator
    # equal to get_users = db_logging(get_users), but more elegant
 
    @db_logging
    def get_prompt_data(self):
        return self.db.get_dashboard_global()
    
    @db_logging
    def get_category_data(self):
        return self.db.get_dashboard_by_column("category")
    
    @db_logging
    def get_model_data(self):
        return self.db.get_dashboard_by_column("model")
    
    @db_logging
    def get_all_data(self):
        return self.db.get_all_data()
    
    @db_logging
    def get_token(self, token_hash):
        return self.db.get_token(token_hash)
    
    # @db_logging
    # def get_last_download(self, user_id):
    #     return self.db.get_last_download(user_id)
    
   

    
    
    
    
