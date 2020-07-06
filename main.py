import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from routes import search, authentication

app = FastAPI()

app.include_router(search.router)
app.include_router(authentication.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
