from typing import List
from pydantic import BaseModel
from .pagination import Pagination 
class SubjectBase(BaseModel):
    name: str
    foreign_name: str
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

class SubjectsResponseModel(BaseModel):
    data: List[SubjectInDB]
    pagination: Pagination

class BasicSubjectInfo(BaseModel):
    id: int
    name: str
    foreign_name: str

    class Config:
        orm_mode = True