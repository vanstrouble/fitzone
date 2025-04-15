from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AdminRoles:
    ADMIN = "admin"
    MANAGER = "manager"


DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin",
    "role": AdminRoles.ADMIN,
}


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    email = Column(String)
    phone = Column(String)
    membership_type = Column(String)
    renovation_date = Column(DateTime)
    created_at = Column(DateTime)


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
    created_at = Column(DateTime)
    admin_username = Column(String, ForeignKey("admins.username"), nullable=True)
    admin = relationship("AdminDB", back_populates="trainer")


class AdminDB(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String(128))
    role = Column(String)
    created_at = Column(DateTime)
    trainer = relationship("TrainerDB", back_populates="admin", uselist=False)

    @property
    def is_admin(self):
        return self.role == AdminRoles.ADMIN

    @property
    def is_manager(self):
        return self.role == AdminRoles.MANAGER
