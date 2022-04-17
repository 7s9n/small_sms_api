from typing import List
from pydantic import BaseModel
from .subject import SubjectInDB
from .grade import GradeInDB


class Base(BaseModel):
    grade_id: int
    subject_id: int


class GradeSubjectOutBase(BaseModel):
    grade: GradeInDB

    class Config:
        orm_mode = True


class GradeSubjectsOut(GradeSubjectOutBase):
    subjects: List[SubjectInDB]


class GradeSubjectOut(GradeSubjectOutBase):
    subject: SubjectInDB


class GradeSubjectCreate(Base):
    pass


class GradeSubjectUpdate(Base):
    pass
