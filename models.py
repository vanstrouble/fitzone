from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AdminRoles:
    ADMIN = "admin"
    MANAGER = "manager"


DEFAULT_ADMIN = {
    "username": "admin",
    "password": "admin",
    "role": AdminRoles.ADMIN,
}


class PersonDB(Base):
    """Base class for entities representing people"""
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    age = Column(Integer)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    # Discriminator field to identify the type of person
    type = Column(String(20))

    __mapper_args__ = {
        "polymorphic_identity": "person",
        "polymorphic_on": type
    }


class UserDB(PersonDB):
    """Gym users/members"""
    __tablename__ = "users"

    id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    membership_type = Column(String)
    renovation_date = Column(DateTime)

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }


class TrainerDB(PersonDB):
    """Gym trainers"""
    __tablename__ = "trainers"

    id = Column(Integer, ForeignKey("persons.id"), primary_key=True)
    specialty = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    admin_username = Column(String, ForeignKey("admins.username"), nullable=True)

    # Relationship with admin
    admin = relationship("AdminDB", back_populates="trainer")

    __mapper_args__ = {
        "polymorphic_identity": "trainer",
    }


class AdminDB(Base):
    """System administrators"""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship with trainer
    trainer = relationship("TrainerDB", back_populates="admin", uselist=False)

    @property
    def is_admin(self):
        return self.role == AdminRoles.ADMIN

    @property
    def is_manager(self):
        return self.role == AdminRoles.MANAGER
