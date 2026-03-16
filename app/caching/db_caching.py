from services.retrieval import Retrieval
import json
import os

DATA_DIR = "static/data"
os.makedirs(DATA_DIR, exist_ok=True)

db = Retrieval()
def db_dump():
    data_set = db.get_all_data()

    with open(f"{DATA_DIR}/AI_monitor_dataset.json", "w") as f:
        json.dump(data_set, f)
