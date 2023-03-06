from sqlalchemy import (
    Column,
    Boolean,
    BigInteger,
    ForeignKey,
    String,
    Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

# from app.models.person import Person
from app.db.base import Base

# class User(Base):
#     id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=False)
#     full_name = Column(String, index=True, nullable=False)
#     username = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_active = Column(Boolean(), default=True)
#     is_superuser = Column(Boolean(), default=False)
#     user_type = Column(String(1), nullable=False)

# class User(Base):
#     __table_args__ = (
#         # UniqueConstraint('id', 'discriminator',
#         #                  name='user_id_and_type_uc'),
#         # PrimaryKeyConstraint('id', 'discriminator',
#         #                                  name='user_id_and_type_pk'),

#         CheckConstraint("discriminator in ('T','S','A') "),
#     )

#     id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
#     first_name = Column(String, nullable=False)
#     father_name = Column(String, nullable=False)
#     gfather_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     gender = Column(Boolean, default=True, nullable=False)
#     date_of_birth = Column(Date, nullable=False)
#     nationality_id = Column(ForeignKey('nationalities.id'), nullable=False)
#     username = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
#     is_active = Column(Boolean(), default=True)
#     discriminator = Column(String(1), nullable=False)

#     __mapper_args__ = {'polymorphic_on': discriminator}

#     nationality = relationship('Nationality', back_populates='users')

# class User(Person):
#     id = Column(BigInteger, ForeignKey('people.id'), primary_key=True)
#     is_superuser = Column(Boolean(), default=False)
#     __mapper_args__ = {'polymorphic_identity': 'U'}

class User(Base):
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    gfather_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Boolean, default=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    nationality_id = Column(ForeignKey('nationalities.id'), nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(String(1), nullable=False)


    nationality = relationship('Nationality', back_populates='users')
    registrations = relationship('Registration', back_populates='student')
    teacher_assigned_grades_and_subjects = relationship('AssignedTeacher', back_populates='teacher')

    @hybrid_property
    def full_name(self)-> str:
        return self.first_name + ' ' + self.father_name + ' ' + self.gfather_name + ' ' + self.last_name