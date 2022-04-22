from typing import List
from pydantic import BaseModel


class GradeBase(BaseModel):
    name: str
    numeric_value: int


class GradeCreate(GradeBase):
    pass


class GradeUpdate(GradeBase):
    pass


class GradeInDB(GradeBase):
    id: int

    class Config:
        orm_mode = True
