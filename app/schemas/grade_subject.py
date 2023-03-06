from typing import List
from pydantic import BaseModel
from .subject import BasicSubjectInfo
from .grade import (
    BasicGradeInfo,
    GradeInDB,
)
from .pagination import Pagination

class Base(BaseModel):
    grade_id: int
    subject_id: int


class GradeSubjectOutBase(BaseModel):
    grade: BasicGradeInfo

    class Config:
        orm_mode = True


class GradeSubjectsOut(GradeSubjectOutBase):
    subjects: List[BasicSubjectInfo]


class GradeSubjectOut(GradeSubjectOutBase):
    subject: BasicSubjectInfo


class GradeSubjectCreate(Base):
    pass


class GradeSubjectUpdate(Base):
    pass

class SubjectsGradeSchema(GradeInDB):
    subjects: List[BasicSubjectInfo]

class SubjectGradePaginatedResponseModel(BaseModel):
    data: List[SubjectsGradeSchema]
    pagination: Pagination

    class Config:
        orm_mode = True