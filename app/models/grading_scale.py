from sqlalchemy import (
    Column,
    String,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.types import SmallInteger
from app.db.base_class import Base


class GradingScale(Base):
    __table_args__ = (
        UniqueConstraint('lowest_percentage', 'highest_percentage', name='_grading_scale_lowest_highest_per_uc'),
        CheckConstraint('lowest_percentage < highest_percentage'),
        )

    id = Column(SmallInteger, primary_key=True, index=True, autoincrement=False)
    name = Column(String, unique=True, index=True, nullable=False)
    lowest_percentage = Column(SmallInteger, nullable=False, default=50)
    highest_percentage = Column(SmallInteger, nullable=False, default=100)
    notes = Column(String, nullable=True)
    