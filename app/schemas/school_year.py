from typing import List
from datetime import date
from datetime import datetime
from pydantic import (
    BaseModel,
    validator,
)
from .pagination import Pagination


class Base(BaseModel):
    title: str
    start_date: date
    end_date: date

    @validator("title")
    def validate_title(cls, value: str):
        if not value:
            raise ValueError('Title must not be empty.')
        return value.strip()

    @validator("start_date", pre=True)
    def parse_start_date(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    @validator("end_date", pre=True)
    def parse_end_date(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    @validator("end_date")
    def validate_start_and_end_date(cls, v, values):
        if values['start_date'] >= v:
            raise ValueError('End date is bigger than or equal to start date.')
        return v


class SchoolYearCreate(Base):
    pass


class SchoolYearUpdate(Base):
    pass


class SchoolYearInDB(Base):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class SchoolYearResponseModel(BaseModel):
    data: List[SchoolYearInDB]
    pagination: Pagination
