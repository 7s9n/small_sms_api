from typing import List, Optional
from pydantic import BaseModel
from .pagination import Pagination 

class LevelBase(BaseModel):
    name: str
    notes: Optional[str] = None

class LevelCreate(LevelBase):
    pass

class LevelUpdate(LevelBase):
    pass

class LevelInDB(LevelBase):
    id: int

    class Config:
        orm_mode = True

class LevelsResponseModel(BaseModel):
    data: List[LevelInDB]
    pagination: Pagination