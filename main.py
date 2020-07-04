import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


@app.get("/search")
async def search(request: Request, keyword: str):
    print(keyword)
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
