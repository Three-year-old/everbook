import hashlib

from fastapi import APIRouter, Request, Depends, Form, Response, HTTPException
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from sql_app.crud import create_user, username_is_exist, email_is_exist
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


@router.post("/everbook/register")
async def register_user(request: Request, response: Response, username: str = Form(...), email: str = Form(...),
                        password: str = Form(...), db: Session = Depends(get_db)):
    md5 = hashlib.md5()
    md5.update(bytes(password, encoding="utf-8"))
    password = md5.hexdigest()
    db_user = create_user(db=db, username=username, email=email, password=password)
    return templates.TemplateResponse("index.html", {
        "code": 0,
        "msg": "注册成功",
        "user": db_user
    })


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
