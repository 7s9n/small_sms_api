from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Nationality(Base):
    id = Column(Integer, primary_key=True, autoincrement=False)
    masculine_form = Column(String, unique=True, nullable=False)
    feminine_form = Column(String, unique=True, nullable=False)
    notes = Column(Text, nullable=True)

    # students = relationship('Student', back_populates='nationality')
    users = relationship('User', back_populates='nationality')
    # people = relationship('Person', back_populates='nationality')
