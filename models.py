from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    email = Column(String)
    phone = Column(String)
    membership_type = Column(String)


class TrainerDB(Base):
    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    email = Column(String)
    phone = Column(String)
    specialty = Column(String)
    start_time = Column(String)
    end_time = Column(String)


class AdminDB(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)
    role = Column(String)
    created_at = Column(DateTime)
