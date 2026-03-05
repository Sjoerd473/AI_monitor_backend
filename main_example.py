from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts.energy_calc import compute_environmental_impact


app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
         
batch = []
BATCH_LENGTH = 1

# keep appending data to be inserted into DB to batch, and then commit it all at once when length is reached, or a time limit


@app.post("/events")
async def receive_event(request: Request):
    data = await request.json()
    print("Received event:", data)

    impact_data = compute_environmental_impact(data)
    print(impact_data)
 
    return {"status": "received"}




@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
 
    return templates.TemplateResponse("index.html", {"request": request,})

# @app.get("/api/<endpoint>")
# def get_<endpoint>():
#     query DB
#     process/aggregate
#     return JSON


# GET /api/prompts/summary → returns JSON like:
# {
#   "top_categories": {"creative": 500, "technical": 524, "funny": 200}
# }



# this would be caching inside main.py, maybe not what I want
# Instead, have these endpoints read from a json file, not the DB
# import time

# cache = {}
# last_update = 0
# CACHE_TTL = 3600  # seconds, 1 hour

# @app.get("/api/prompts/summary")
# def get_summary():
#     global last_update
#     if time.time() - last_update > CACHE_TTL or "summary" not in cache:
#         # fetch from DB
#         cache["summary"] = fetch_summary_from_db()
#         last_update = time.time()
#     return cache["summary"]