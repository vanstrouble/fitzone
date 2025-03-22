from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import DateTime

Base = declarative_base()


class PersonDB(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Discriminator to identify the type of person
    type = Column(String(50))

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "person"}


class UserDB(PersonDB):
    __tablename__ = "users"

    id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    membership_type = Column(String(50))

    __mapper_args__ = {"polymorphic_identity": "user"}


class TrainerDB(PersonDB):
    __tablename__ = "trainers"

    id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    specialty = Column(String(100))
    start_time = Column(String(10))
    end_time = Column(String(10))

    __mapper_args__ = {"polymorphic_identity": "trainer"}


class AdminDB(PersonDB):
    __tablename__ = "admins"

    id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False)  # superadmin, admin

    __mapper_args__ = {"polymorphic_identity": "admin"}
