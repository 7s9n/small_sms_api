from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Nationality(Base):
    id = Column(Integer, primary_key=True)
    masculine_form = Column(String, unique=True, nullable=False)
    feminine_form = Column(String, unique=True, nullable=False)
    notes = Column(Text, nullable=True)

    students = relationship('Student', back_populates='nationality')
