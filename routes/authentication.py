import hashlib

from fastapi import APIRouter, Request, Depends, Form, Response
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

from sql_app.crud import create_user, username_is_exist, email_is_exist, set_cookie, get_login_user
from sql_app.database import SessionLocal

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
    })


@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
    })


@router.post("/register")
async def register_user(request: Request, response: Response, username: str = Form(...), email: str = Form(...),
                        password: str = Form(...), db: Session = Depends(get_db)):
    md5 = hashlib.md5()
    md5.update(bytes(password, encoding="utf-8"))
    password = md5.hexdigest()
    db_user = create_user(db=db, username=username, email=email, password=password)
    set_cookie(response=response, username=username, email=email)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/login")
async def login_user(request: Request, response: Response, username: str = Form(...), password: str = Form(...),
                     db: Session = Depends(get_db)):
    user = get_login_user(db=db, username=username, password=password)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "用户名或密码不正确"
        })
    response.set_cookie(key="test", value="cookie")
    set_cookie(response=response, username=user.username, email=user.email)
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/everbook/examine/username")
async def examine_username(name: str = Form(...), db: Session = Depends(get_db)):
    # 用户名是否重复
    username_exist = username_is_exist(username=name, db=db)
    if username_exist:
        return {
            "code": 1,
            "msg": "用户名已存在"
        }
    return {
        "code": 0,
        "msg": name,
    }


@router.post("/everbook/examine/email")
async def examine_email(email: str = Form(...), db: Session = Depends(get_db)):
    # 邮箱是否注册
    email_exist = email_is_exist(email=email, db=db)
    if email_exist:
        return {
            "code": 1,
        }
    return {
        "code": 0,
    }
