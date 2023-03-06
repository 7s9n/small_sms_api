from typing import List, Optional
from pydantic import (
    BaseModel,
    root_validator,
)
from .pagination import Pagination 

class GradingScaleBase(BaseModel):
    name: str
    lowest_percentage: float
    highest_percentage: float
    notes: Optional[str] = None

    @root_validator
    def check_passwords_match(cls, values):
        lowest, highest = values.get('lowest_percentage'), values.get('highest_percentage')
        if lowest is not None and highest is not None and lowest > highest:
            raise ValueError('النسبة الصغرى اكبر من النسبة الكبرى.')
        return values

class GradingScaleCreate(GradingScaleBase):
    pass

class GradingScaleUpdate(GradingScaleBase):
    pass

class GradingScaleInDB(GradingScaleBase):
    id: int

    class Config:
        orm_mode = True

class GradingScalesResponseModel(BaseModel):
    data: List[GradingScaleInDB]
    pagination: Pagination