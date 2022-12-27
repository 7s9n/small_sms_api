from sqlalchemy import (
    Column,
    String,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class Subject(Base):
    id = Column(SmallInteger, primary_key=True, index=True, nullable=False)
    name = Column(String, unique=True, index=True, nullable=False)
    add_to_total = Column(Boolean, default=True, nullable=False)
    higher_score = Column(SmallInteger, default=100)
    lower_score = Column(SmallInteger, default=50)
    grades = relationship(
        'GradeSubject', back_populates='subject', cascade="all, delete-orphan")
