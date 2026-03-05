from services.base_service import BaseService

class Ingestion(BaseService):
    

    def batch_insert(self, batch):
        self.db.insert_prompts(batch) ## all these functions should be called in a try except block, to handle the original error



