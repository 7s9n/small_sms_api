from sqlalchemy import (
    Column,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class Level(Base):
    id = Column(SmallInteger, primary_key=True, index=True, nullable=False, autoincrement=False)
    name = Column(String, unique=True, index=True, nullable=False)
    notes = Column(String, nullable=True)

    grades = relationship("Grade", back_populates='level', lazy="selectin")