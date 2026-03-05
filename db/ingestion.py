from db.promptdb import PromptDB

class Ingestion:
    def __init__(self):
        self.db = PromptDB()

    def batch_insert(self, batch):
        self.db.insert_prompts(batch) ## all these functions should be called in a try except block, to handle the original error



