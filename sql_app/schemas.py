from pydantic import BaseModel


class BlackListBase(BaseModel):
    domain: str


class BlackListCreate(BlackListBase):
    pass


class BlackList(BlackListBase):
    id: int

    class Config:
        orm_mode = True

