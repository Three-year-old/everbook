# FastAPI
FastAPI 是一个用于构建 API 的现代、快速（高性能）的 web 框架，使用 Python 3.6+ 并基于标准的 Python 类型提示。

## Templates
`fastapi`主要用来构建接口，但也可以渲染模板引擎，若采用`jinja2`模板引擎，首先需要安装依赖
```commandline
pip instal jinja2
``` 
一些静态文件也可以被导入，需要安装`aiofiles`依赖
```commandline
pip install aiofiles
```
在视图文件中引入`jinja2`引擎
```python
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
```
这样就可以在项目根目录下的`templates`文件夹内存放`html`文件了。

渲染语法和`jinja2`基本一致，不过在返回`html`文件时，需要返回`Request`对象
```python
@router.get("/")
async def read_root(request: Request, username: Optional[str] = Cookie(None)):
    if username:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "username": username,
        })
    return templates.TemplateResponse("index.html", {
        "request": request,
    })
```

## SQL
`sql`文件位于`sql_app`文件夹下
```commandline
.
└── sql_app
    ├── __init__.py
    ├── create.py
    ├── crud.py
    ├── database.py
    ├── models.py
    └── schemas.py
```
`models.py`定义了数据模型，对应了数据库中的表结构。

`shcemas.py`是一些操作数据库的工具类。

`crud.py`定义了操作数据库的方法。

`database.py`是数据库的相关配置。

最终运行`create.py`，可以在项目根目录下生成数据库文件。为了测试，我添加了测试用户数据

| 用户名 |   密码   |    
| ---- | ----|
|`everbook`|`forabetternovelreadingexperience`|

## Cookie
关于用户登录，我采用了最简单的`cookie`验证，在登录成功时，写入相关`cookie`。

`fastapi`中提供了`cookie`的操作接口，在`Response`类中定义了`set_cookie`方法。具体使用在[`crud.py`](../sql_app/crud.py)文件中
```python
def set_cookie(response: Response, username: str, email: str, id: str):
    """
    设置cookie
    :param id:
    :param response:
    :param username:
    :param email:
    :return:
    """
    response.set_cookie(key="login_status", value=str(uuid.uuid1()))
    response.set_cookie(key="username", value=username)
    response.set_cookie(key="email", value=email)
    response.set_cookie(key="id", value=id)
```
当需要判断是否登录时，对应的视图函数中应该加入[`Cookie Parameters`](https://fastapi.tiangolo.com/tutorial/cookie-params/)
```python
@router.get("/")
async def read_root(request: Request, username: Optional[str] = Cookie(None)):
    if username:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "username": username,
        })
    return templates.TemplateResponse("index.html", {
        "request": request,
    })
```
在方法中添加`username: Optional[str] = Cookie(None)`这一参数，如果参数不为空，则将`username`一同返回给前端，否则不返回。

## API
`fastapi`提供了类似`swagger2`的调试接口，当你在本地启动`fastapi`框架后，可以访问[localhost:8000/docs](http://localhost:8000/docs) 来查看定义的API

## More
更多细节参考`fastapi`[官方文档](https://fastapi.tiangolo.com/)