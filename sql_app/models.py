from sqlalchemy import Column, Integer, String

from .database import Base


class BlackDomain(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String)


class Rule(Base):
    __tablename__ = "rule"

    id = Column(Integer, primary_key=True, index=True)
    netloc = Column(String)
    """
    choice
    0: 表示章节网页需要当前页面url拼接
    1: 表示章节链接使用本身自带的链接，不用拼接
    2: 用域名进行拼接
    """
    choice = Column(Integer)
    chapter_tag = Column(String)
    chapter_value = Column(String)
    content_tag = Column(String)
    content_value = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)


class Shelf(Base):
    __tablename__ = "shelf"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    book = Column(String)
