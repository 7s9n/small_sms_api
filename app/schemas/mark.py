from typing import List, Optional
from pydantic import BaseModel
from .pagination import Pagination 
from enum import IntEnum

class MonthEnum(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

class SemasterEnum(IntEnum):
    FIRST_SEMASTER = 1
    SECOND_SEMASTER = 2

class MarkBase(BaseModel):
    student_id: int
    grade_id: int
    subject_id: int
    semaster: SemasterEnum
    month: MonthEnum
    # note: Optional[str] = None

    class Config:
        use_enum_values = True

class Marks(BaseModel):
    written_test: int
    oral_test: int
    homeworks: int
    attendance: int

class MarkCreateRequest(Marks, MarkBase):
    pass

class BaseFinalMark(BaseModel):
    exam: int

class FinalMark(BaseFinalMark):
    student_id: int
    subject_id: int
    semaster: int

class FinalMarkCreateRequest(FinalMark):
    grade_id: int

class FinalMarkCreateInDB(FinalMark, BaseFinalMark):
    school_year_id: int

    class Config:
        orm_mode = True

class FinalMarkUpdate(BaseFinalMark):
    pass


class MarkCreateInDB(MarkCreateRequest):
    school_year_id: int

    class Config:
        orm_mode = True

class MarkUpdate(Marks):
    pass

class MarkInDB(MarkBase,Marks):
    student_name: str
    grade_name: str
    subject_name: str
    school_year_id: int
    school_year_title: str
    total: float
    monthly_outcome: float
    grading: Optional[str] = None

    class Config:
        orm_mode = True

class MarksResponseModel(BaseModel):
    data: List[MarkInDB]
    pagination: Pagination