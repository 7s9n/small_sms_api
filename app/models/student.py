from sqlalchemy import (
    Column,
    String,
    Date,
    Boolean,
)
from sqlalchemy.types import BigInteger
from app.db.base_class import Base


class Student(Base):
    id = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    gfather_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Boolean, default=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
