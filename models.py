from sqlalchemy import Column, Integer, String, TIMESTAMP
from database import Base, engine
from datetime import datetime


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True)
    phone = Column(String)
    membership_type = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.today().date())


Base.metadata.create_all(bind=engine)
