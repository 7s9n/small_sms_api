from typing import Optional
from pydantic import BaseModel

class SubjectBase(BaseModel):
    name: str
    add_to_total: bool = True,
    higher_score: int = 100
    lower_score: int = 50


class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    pass

class SubjectInDB(SubjectBase):
    id: int

    class Config:
        orm_mode = True