from sqlalchemy import (
    Column,
    String,
    Date,
    Boolean,
)
from sqlalchemy.types import BigInteger
from app.db.base_class import Base


class SchoolYear(Base):
    id = Column(BigInteger, primary_key=True)
    title = Column(String, index=True, unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
