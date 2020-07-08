import hashlib
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, Response, Cookie
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from starlette.templating import Jinja2Templates

from sql_app.crud import create_user, username_is_exist, email_is_exist, set_cookie, get_login_user, put_book_in_shelf, \
    check_book_in_shelf, get_user_all_book, delete_book_from_shelf
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
    set_cookie(response=response, username=username, email=email, id=db_user.id)
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)


@router.post("/login")
def login_user(request: Request, response: Response, username: str = Form(...), password: str = Form(...),
               db: Session = Depends(get_db)):
    user = get_login_user(db=db, username=username, password=password)
    if not user:
        return {
            "status": 1,
            "msg": "用户名或密码不正确"
        }
    set_cookie(response=response, username=user.username, email=user.email, id=user.id)
    return {
        "status": 0,
        "msg": "登录成功",
    }


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


@router.get("/user")
async def get_user(request: Request, login_status: Optional[str] = Cookie(None),
                   username: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if login_status:
        user = username_is_exist(db=db, username=username)
        book = get_user_all_book(db=db, user_id=user.id)
        return templates.TemplateResponse("user.html", {
            "request": request,
            "username": username,
            "books": book,
        })
    else:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)


@router.post("/favorite/book")
async def mark_book(url: str = Form(...), name: str = Form(...), id: str = Form(...), db: Session = Depends(get_db)):
    if check_book_in_shelf(db=db, url=url):
        return {
            "code": "warning",
            "msg": "已经在书架中了"
        }
    book = put_book_in_shelf(url=url, name=name, db=db, id=id)
    if book:
        return {
            "code": "success",
            "msg": "加入书架成功"
        }
    return {
        "code": "error",
        "msg": "未知错误"
    }


@router.post("/delete/book")
async def delete(url: str = Form(...), db: Session = Depends(get_db)):
    if delete_book_from_shelf(db=db, url=url):
        return {
            "code": "success",
            "msg": "删除成功",
        }
    return {
        "code": "error",
        "msg": "该书不存在",
    }
