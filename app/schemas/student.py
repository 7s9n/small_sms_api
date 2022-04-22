import re
from datetime import date
from datetime import datetime
from pydantic import (
    BaseModel,
    validator
)


class Base(BaseModel):
    first_name: str
    father_name: str
    gfather_name: str
    last_name: str
    gender: bool
    date_of_birth: date
    guardian_phone_no: str

    @validator("first_name")
    def validate_first_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('First name must not be empty.')
        return value

    @validator("father_name")
    def validate_father_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Father name must not be empty.')
        return value

    @validator("gfather_name")
    def validate_gfather_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Grand Father name must not be empty.')
        return value

    @validator("last_name")
    def validate_last_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Last name must not be empty.')
        return value

    @validator("date_of_birth", pre=True)
    def parse_date_of_birth(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()

    @validator("guardian_phone_no")
    def validate_guardian_phone_no(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Guardian phone number must not be empty.')
        if not re.match(r'^\d{9}$', value):
            raise ValueError('Please Enter a valid phone number.')

        return value


class StudentCreate(Base):
    pass


class StudentUpdate(Base):
    pass


class StudentInDB(Base):
    id: int

    class Config:
        orm_mode = True
