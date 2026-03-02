from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from scripts.energy_calc import compute_environmental_impact


app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
         
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

# @app.get('/dati', response_class=HTMLResponse)
# async def boop():
#     return """
#     <html>
#     <p>This is a HTML response</p>
#     </html>


# """


