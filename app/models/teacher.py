from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey
)
from app.models.user import User


# class Teacher(User):
#     id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)

    # __mapper_args__ = {'polymorphic_identity': 'T'}
