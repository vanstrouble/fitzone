from models import PersonDB, UserDB, TrainerDB, AdminDB
from person import Person
from user import User
from trainer import Trainer


def person_to_db(person):
    """Converts a Person object to a PersonDB object"""
    return PersonDB(
        name=person.name, age=person.age, email=person.email, phone=person.phone
    )


def user_to_db(user):
    """Converts a User object to a UserDB object"""
    return UserDB(
        name=user.name,
        age=user.age,
        email=user.email,
        phone=user.phone,
        membership_type=user.membership_type,
    )


def trainer_to_db(trainer):
    """Converts a Trainer object to a TrainerDB object"""
    return TrainerDB(
        name=trainer.name,
        age=trainer.age,
        email=trainer.email,
        phone=trainer.phone,
        specialty=trainer.specialty,
        start_time=trainer.start_time,
        end_time=trainer.end_time,
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
