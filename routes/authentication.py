from fastapi import APIRouter, Request
from starlette.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
    })


@router.get("/register")
def login(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
    })
