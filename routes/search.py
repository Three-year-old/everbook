import time

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from fetch.BaiduCrawler import BaiduCrawler
from fetch.cache import get_novels_chapter, get_novels_content
from fetch.utils import get_netloc
from sql_app import schemas, crud
from sql_app.crud import get_all_blacklist, get_allow_domain, get_rule_by_netloc
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
    """
    利用百度搜索解析结果搜索小说
    :param request:
    :param keyword: 关键词
    :param db:
    :return:
    """
    # 获取过滤黑名单域名
    blacklist = []
    for item in get_all_blacklist(db):
        blacklist.append(item.domain)

    baidu = BaiduCrawler()

    # 获取已解析的域名
    allow = []
    for item in get_allow_domain(db):
        allow.append(item[0])

    start = time.clock()
    results = await baidu.search(keyword=keyword, blacklist=blacklist, allow=allow)
    end = time.clock()
    return templates.TemplateResponse("result.html", {
        "request": request,
        "keyword": keyword,
        "time": round(end - start, 3),
        "results": results,
        "length": len(results),
    })


@router.get("/chapter/")
async def get_book_chapter(request: Request, url: str, db: Session = Depends(get_db)):
    """
    获取小说章节以及其他信息
    :param request:
    :param url: 抓取的小说网站url
    :param db:
    :return:
    """
    netloc = get_netloc(url)
    # 获取已解析的域名
    allow = []
    for item in get_allow_domain(db):
        allow.append(item[0])
    if netloc not in allow:
        return RedirectResponse(url=url)
    rule = get_rule_by_netloc(db=db, netloc=netloc)
    content = await get_novels_chapter(url=url, choice=rule.choice, chapter_tag=rule.chapter_tag,
                                       chapter_value=rule.chapter_value)
    info = [i.strip() for i in content["info"] if i.strip() is not ""]
    novel = info[0]
    info = info[1::]
    intro = [i.strip() for i in content["intro"] if i.strip() is not ""]
    chapters = content["chapter"]
    if content:
        return templates.TemplateResponse("chapter.html", {
            "request": request,
            "url": url,
            "novel": novel,
            "info": info,
            "intro": intro,
            "chapters": chapters,
        })
    else:
        # 解析失败后应返回一个错误页面
        return HTTPException(status_code=404, detail="解析失败")


@router.get("/content")
async def get_chapter_content(request: Request, url: str, novel: str, chapter: str, db: Session = Depends(get_db)):
    netloc = get_netloc(url)
    allow = []
    for item in get_allow_domain(db):
        allow.append(item[0])
    if netloc not in allow:
        return RedirectResponse(url=url)
    rule = get_rule_by_netloc(db=db, netloc=netloc)
    content = await get_novels_content(url=url, content_tag=rule.content_tag, content_value=rule.content_value)
    articles = content["article"]
    pages = content["pages"]
    return templates.TemplateResponse("content.html", {
        "request": request,
        "articles": articles,
        "novel": novel,
        "title": content["title"],
        "chapter": chapter,
        "pages": pages,
    })


@router.post("/create/black", response_model=schemas.BlackList)
def create_blacklist(blacklist: schemas.BlackListCreate, db: Session = Depends(get_db)):
    db_blacklist = crud.get_blacklist(db=db, domain=blacklist.domain)
    if db_blacklist:
        raise HTTPException(status_code=400, detail="Black domain already existed")
    return crud.create_blacklist(db=db, blacklist=blacklist)
