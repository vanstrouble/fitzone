from database import SessionLocal
from models import UserDB, TrainerDB, AdminDB
from converters import db_to_user, db_to_trainer, user_to_db, trainer_to_db
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_user(user):
    """Creates a new user in the database"""
    session = SessionLocal()
    try:
        user_db = user_to_db(user)
        session.add(user_db)
        session.commit()
        user.unique_id = user_db.id
        return user
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        return None
    finally:
        session.close()


def get_user(unique_id):
    """Gets a user by their ID"""
    session = SessionLocal()
    try:
        user_db = session.query(UserDB).filter(UserDB.id == unique_id).first()
        if user_db:
            return db_to_user(user_db)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error getting user: {str(e)}")
        return None
    finally:
        session.close()


def get_all_users():
    """Gets all users"""
    session = SessionLocal()
    try:
        users_db = session.query(UserDB).all()
        return [db_to_user(user_db) for user_db in users_db]
    except SQLAlchemyError as e:
        logger.error(f"Error getting users: {str(e)}")
        return []
    finally:
        session.close()


def update_user(user):
    """Updates an existing user"""
    if not user.unique_id:
        logger.error("Cannot update a user without an ID")
        return False

    session = SessionLocal()
    try:
        user_db = session.query(UserDB).filter(UserDB.id == user.unique_id).first()
        if not user_db:
            logger.warning(f"User with ID {user.unique_id} not found")
            return False

        user_db.name = user.name
        user_db.age = user.age
        user_db.email = user.email
        user_db.phone = user.phone
        user_db.membership_type = user.membership_type

        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating user: {str(e)}")
        return False
    finally:
        session.close()


def delete_user(unique_id):
    """Deletes a user by their ID"""
    session = SessionLocal()
    try:
        user_db = session.query(UserDB).filter(UserDB.id == unique_id).first()
        if not user_db:
            logger.warning(f"User with ID {unique_id} not found")
            return False

        session.delete(user_db)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        return False
    finally:
        session.close()


def create_trainer(trainer):
    """Creates a new trainer in the database"""
    session = SessionLocal()
    try:
        trainer_db = trainer_to_db(trainer)
        session.add(trainer_db)
        session.commit()
        # Update the ID in the domain object
        trainer.unique_id = trainer_db.id
        return trainer
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating trainer: {str(e)}")
        return None
    finally:
        session.close()


# TODO: Implement get_trainer, get_all_trainers, update_trainer, delete_trainer
# following the same pattern
