from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    BigInteger,
    Date,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# class Person(Base):
#     pass
    # __table_args__ = (
    #     CheckConstraint("discriminator in ('S','U')"),
    # )
    
    # id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    # first_name = Column(String, nullable=False)
    # father_name = Column(String, nullable=False)
    # gfather_name = Column(String, nullable=False)
    # last_name = Column(String, nullable=False)
    # gender = Column(Boolean, default=True, nullable=False)
    # date_of_birth = Column(Date, nullable=False)
    # nationality_id = Column(ForeignKey('nationalities.id'), nullable=False)
    # username = Column(String, unique=True, index=True, nullable=False)
    # password = Column(String, nullable=False)
    # is_active = Column(Boolean(), default=True)
    # discriminator = Column(String(1), nullable=False)

    # __mapper_args__ = {'polymorphic_on': discriminator}

    # nationality = relationship('Nationality', back_populates='people')
