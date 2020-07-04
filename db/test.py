# 创建数据库
import sqlite3

# 连接到数据库
# 数据库文件是“everbook.db”
# 如果数据库不存在的话，将会自动创建一个数据库
conn = sqlite3.connect("everbook.db")
