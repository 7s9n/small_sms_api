from datetime import datetime
from typing import List
from pydantic import (
    BaseModel,
    Field,
)
from .student import StudentInDB
from .grade import GradeInDB
from .school_year import SchoolYearInDB
from .pagination import Pagination

class Base(BaseModel):
    student_id: int
    grade_id: int
    school_year_id: int

class RegistrationCreate(Base):
    pass


class RegistrationUpdate(Base):
    pass


class RegistrationIn(BaseModel):
    student_id: int
    grade_id: int


class RegistrationOut(BaseModel):
    student: StudentInDB = Field(..., include={"id", "full_name"})
    grade: GradeInDB = Field(..., include={"id", "composite_name"})
    school_year: SchoolYearInDB = Field(..., include={"id", "title"})
    created_at: datetime

    class Config:
        orm_mode = True
        fields = {'created_at': {'include': True}}

class RegistrationsResponseModel(BaseModel):
    data: List[RegistrationOut] 
    pagination: Pagination

    class Config:
        orm_mode = True
