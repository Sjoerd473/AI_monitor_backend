from services.base_service import BaseService

class Retrieval(BaseService):

    def get_users(self):
        return self.db.get_users() ## all these functions should be called in a try except block, to handle the original error

test = Retrieval()

print(test.get_users())