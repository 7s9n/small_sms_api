from typing import (
    Optional,
    List,
)
from pydantic import (
    BaseModel,
    validator,
)
from .pagination import Pagination 


class Base(BaseModel):
    masculine_form: str
    feminine_form: str
    notes: Optional[str] = None

    @validator("masculine_form")
    def validate_masculine_form(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Masculine form must not be empty.')
        return value

    @validator("feminine_form")
    def validate_feminine_form(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError('Feminine form must not be empty.')
        return value


class NationalityCreate(Base):
    pass


class NationalityUpdate(Base):
    pass


class NationalityInDB(Base):
    id: int

    class Config:
        orm_mode = True

class NationalitiesResponseModel(BaseModel):
    data: List[NationalityInDB]
    pagination: Pagination