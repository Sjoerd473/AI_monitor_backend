# this is the class that writes to the DB
# all the SQL is abstracted away in promptdb
# will probably be very short, but seperation of concerns is important

from services.base_service import BaseService, db_logging

class Ingestion(BaseService):
    # this is the syntax for a decorator
    # equal to batch_insert = db_logging(batch_insert), but more elegant
    @db_logging
    def batch_insert(self, batch):
        self.db.insert_prompts(batch) 

    @db_logging
    def insert_token(self, user_id, token_hash):
        self.db.insert_token(user_id, token_hash)

    @db_logging
    def update_token_last_used(self, token_hash):
        self.db.update_token_last_used(token_hash)

    # @db_logging
    # def log_download(self, user_id):
    #     self.db.log_download(user_id)
        
    @db_logging
    def insert_user(self, user_id):
        self.db.insert_user(user_id)


    @db_logging
    def batch_update_last_used(self, token_hashes: list):
        self.db.batch_update_last_used(token_hashes)



