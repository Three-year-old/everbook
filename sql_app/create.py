from sql_app import models
from sql_app.database import engine

# 创建数据库
# 此时运行python create.py会在当前目录下创建一个everbook.db数据库文件
# 运行fastAPI项目时，由于main.py文件与该文件不在同一目录，所以会在项目根目录下再次创建一个数据库文件
# 因此该文件不必再运行
models.Base.metadata.create_all(bind=engine)
