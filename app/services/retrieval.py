# this is the class that reads from the DB
# all the SQL is abstracted away in promptdb.py

from services.base_service import BaseService, db_logging

class Retrieval(BaseService):
    # all these methods will call methods inside promptdb
    # this is the syntax for a decorator
    # equal to get_users = db_logging(get_users), but more elegant
    @db_logging
  
    
    # def get_prompt_impact(self, type):
    #     match type:
    #         case 'co2':
    #             return self.db.get_CO2('hour'), self.db.get_CO2('day'), self.db.get_CO2('week') 
    #         case 'water':
    #             return self.db.get_water('hour'), self.db.get_water('day'), self.db.get_water('week')
    #         case 'energy':
    #             return self.db.get_energy('hour'), self.db.get_energy('day'), self.db.get_energy('week')
    def get_prompt_data(self):
        return self.db.get_dashboard_global()
    
    def get_category_data(self):
        return self.db.get_dashboard_by_column("category")
    
    def get_model_data(self):
        return self.db.get_dashboard_by_column("model")
    
   

    
    
    
    
   

# this is just for testing, to be deleted
if __name__ == "__main__":
    r = Retrieval()
    
