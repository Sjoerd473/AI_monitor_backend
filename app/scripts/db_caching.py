from services.retrieval import Retrieval
import json

db = Retrieval()

dashboard = {
    "prompts" : db.get_prompt_data(),
    "categories": db.get_category_data(),
    "models": db.get_model_data()
}

with open("static/data/dashboard.json", "w") as f:
  json.dump(dashboard, f)


# prompt= 'SELECT json_build_object('

# queries= [
#     db.get_prompt_impact("co2"),
#     db.get_prompt_impact("water"),
#     db.get_prompt_impact("energy")
# ]

# for a in queries:
#     for b in a:
#         for c in b:
#             prompt += c
# prompt = prompt[0:-9]
# prompt += ')'
# print(prompt)
# this file will query the DB for the data we need, then save it in a .json file
# it'll be a cron job running every hour(?) 
# this way our application does not need to query the DB often at all

# a list of functions that compile an sql query
# then send it to the DB to get one single json file

# cur.execute(sql)
# dashboard_data = cur.fetchone()[0]
# or
# dashboard_data = cur.fetchall()[0][0], because we don't have a fetchone in the DB class

# with open("static/data/dashboard.json", "w") as f:
#     json.dump(dashboard_data, f)

