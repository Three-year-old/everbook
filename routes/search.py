from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from sql_app import schemas, crud
from sql_app.crud import get_all_blacklist
from sql_app.database import SessionLocal

templates = Jinja2Templates(directory="templates")

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


@router.get("/search")
async def search(request: Request, keyword: str, db: Session = Depends(get_db)):
    print(get_all_blacklist(db))
    return templates.TemplateResponse("index.html", {
        "request": request,
    })


@router.post("/create/black", response_model=schemas.BlackList)
def create_blacklist(blacklist: schemas.BlackListCreate, db: Session = Depends(get_db)):
    db_blacklist = crud.get_blacklist(db=db, domain=blacklist.domain)
    if db_blacklist:
        raise HTTPException(status_code=400, detail="Black domain already existed")
    return crud.create_blacklist(db=db, blacklist=blacklist)
