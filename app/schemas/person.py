from typing import Optional, List
from datetime import date
from datetime import datetime

from pydantic import (
    BaseModel,
    validator,
    constr
)
from app.schemas.nationality import NationalityInDB


class PersonBase(BaseModel):
    first_name: str
    father_name: str
    gfather_name: str
    last_name: str
    gender: bool
    date_of_birth: date
    nationality_id: int
    is_active: Optional[bool] = True
    username: str
    
    
    @validator("first_name")
    def validate_first_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('الاسم الأول يجب ألا يكون فارغًا.')
        return value

    @validator("father_name")
    def validate_father_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('لا يجب ترك اسم الأب فارغًا.')
        return value

    @validator("gfather_name")
    def validate_gfather_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('لا يجب ترك اسم الجد فارغًا.')
        return value

    @validator("last_name")
    def validate_last_name(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('الاسم الأخير يجب ألا يكون فارغًا.')
        return value

    @validator("date_of_birth", pre=True)
    def parse_date_of_birth(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(
            value,
            "%Y-%m-%d"
        ).date()
    
    @validator("username")
    def validate_username(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('.إسم المستخدم يجب الأ يكون فارغاً')
        return value.lower()



class PersonCreate(PersonBase):
    password: str


class PersonUpdate(PersonBase):
    password: Optional[str] = None

class AdminTeacherCreate(PersonCreate):
    discriminator: constr(min_length=1, max_length=1, strip_whitespace=True, regex=r"[A|T|a|t]")

    @validator("discriminator")
    def validate_discriminator(cls, value: str):
        return value.upper()

class AdminTeacherUpdate(PersonBase):
    password: Optional[str] = None

class PersonInDBase(PersonBase):
    id: int
    nationality: NationalityInDB
    
    class Config:
        orm_mode = True


class PersonInDB(PersonInDBase):
    hashed_password: str
