from models import UserDB, TrainerDB, AdminDB
from person import Person
from user import User
from trainer import Trainer
from admin import Admin
from datetime import datetime


def user_to_db(user):
    """Converts a User object to a UserDB object"""
    # Convertir strings a objetos datetime
    created_at = (
        datetime.strptime(user.created_at, "%Y-%m-%d %H:00")
        if user.created_at
        else None
    )
    renovation_date = (
        datetime.strptime(user.renovation_date, "%Y-%m-%d %H:00")
        if user.renovation_date
        else None
    )

    return UserDB(
        name=user.name,
        lastname=user.lastname,
        age=user.age,
        email=user.email,
        phone=user.phone,
        membership_type=user.membership_type,
        renovation_date=renovation_date,
        created_at=created_at,
    )


def trainer_to_db(trainer):
    """Converts a Trainer object to a TrainerDB object"""
    created_at = (
        datetime.strptime(trainer.created_at, "%Y-%m-%d %H:00")
        if trainer.created_at
        else None
    )

    return TrainerDB(
        name=trainer.name,
        lastname=trainer.lastname,
        age=trainer.age,
        email=trainer.email,
        phone=trainer.phone,
        specialty=trainer.specialty,
        start_time=trainer.start_time,
        end_time=trainer.end_time,
        created_at=created_at,
    )


def admin_to_db(admin):
    """Converts an Admin object to an AdminDB object"""
    created_at = (
        datetime.strptime(admin.created_at, "%Y-%m-%d %H:00")
        if isinstance(admin.created_at, str)
        else admin.created_at
    )

    return AdminDB(
        username=admin.username,
        password_hash=admin.password,
        role=admin.role,
        created_at=created_at,
    )


def db_to_person(person_db):
    """Converts a PersonDB object to a Person object"""
    return Person(
        name=person_db.name,
        age=person_db.age,
        email=person_db.email,
        phone=person_db.phone,
    )


def db_to_user(user_db):
    """Converts a UserDB object to a User object"""
    return User(
        unique_id=user_db.id,
        name=user_db.name,
        age=user_db.age,
        email=user_db.email,
        phone=user_db.phone,
        membership_type=user_db.membership_type,
    )


def db_to_trainer(trainer_db):
    """Converts a TrainerDB object to a Trainer object"""
    return Trainer(
        unique_id=trainer_db.id,
        name=trainer_db.name,
        age=trainer_db.age,
        email=trainer_db.email,
        phone=trainer_db.phone,
        specialty=trainer_db.specialty,
        start_time=trainer_db.start_time,
        end_time=trainer_db.end_time,
    )


def db_to_admin(admin_db):
    """Converts an AdminDB object to an Admin object"""
    admin = Admin(
        username=admin_db.username,
        password=admin_db.password_hash,
        role=admin_db.role,
        created_at=admin_db.created_at,
    )
    admin.unique_id = admin_db.id  # Establecemos el ID después de crear el objeto
    return admin
