from services.retrieval import Retrieval
import json

db = Retrieval()
def db_dump():
    data_set = db.get_all_data()

    with open("static/data/AI_monitor_dataset.json", "w") as f:
        json.dump(data_set, f)
