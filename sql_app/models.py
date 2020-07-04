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
    choice = Column(Integer)
    chapter_tag = Column(String)
    chapter_value = Column(String)
    content_tag = Column(String)
    content_value = Column(String)
