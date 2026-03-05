# this is the class that writes to the DB
# all the SQL is abstracted away in promptdb
# will probably be very short, but seperation of concerns is important

from services.base_service import BaseService, db_logging

class Ingestion(BaseService):
    # this is the syntax for a decorator
    # equal to batch_insert = db_logging(batch_insert), but more elegant
    @db_logging
    def batch_insert(self, batch):
        self.db.insert_prompts(batch) ## all these functions should be called in a try except block, to handle the original error



