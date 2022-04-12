from sqlalchemy import (
    Column,
    String,
)
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class Grade(Base):
    id = Column(SmallInteger, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
