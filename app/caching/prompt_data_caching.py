from services.retrieval import Retrieval
import json

db = Retrieval()
def prompt_dump():
  dashboard = {
      "prompts" : db.get_prompt_data(),
      "categories": db.get_category_data(),
      "models": db.get_model_data()
  }
  
  models = db.get_models_table()
  
  with open("static/data/dashboard.json", "w") as f:
    json.dump(dashboard, f)
  
  with open("static/data/models.json", "w") as f:
    json.dump(models, f) 


# this file will query the DB for the data we need, then save it in a .json file
# it'll be a cron job running every hour(?) 
# this way our application does not need to query the DB often at all

# a list of functions that compile an sql query
# then send it to the DB to get one single json file



