import logging
from sqlalchemy.exc import SQLAlchemyError
from prettytable import PrettyTable
from controllers.database import SessionLocal
from models.models import DEFAULT_ADMIN, UserDB, TrainerDB, AdminDB, AdminRoles
from models.admin import Admin
from controllers.converters import (
    admin_to_db,
    db_to_admin,
    db_to_user,
    db_to_trainer,
    user_to_db,
    trainer_to_db,
)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ----- Funciones auxiliares compartidas -----


def _check_admin_username_exists(session, username):
    """Helper function to check if username exists (internal use)"""
    existing_admin = session.query(AdminDB).filter(AdminDB.username == username).first()
    return existing_admin is not None


def has_admin_permission(admin, required_role=AdminRoles.MANAGER):
    """Check if an admin has permissions for a required role"""
    if not admin:
        return False
    if admin.role == AdminRoles.ADMIN:
        return True
    if admin.role == AdminRoles.MANAGER and required_role == AdminRoles.MANAGER:
        return True
    return False


# ----- Funciones de Usuario (User) -----


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


def update_user(user, requester_admin):
    """Updates an existing user"""
    if not requester_admin or not has_admin_permission(
        requester_admin, AdminRoles.MANAGER
    ):
        logger.warning(
            f"Unauthorized update attempt by "
            f"{getattr(requester_admin, 'username', 'Unknown')}"
        )
        return False
    if not getattr(user, "unique_id", None):
        logger.error("Cannot update a user without a valid ID")
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


def debug_print_users():
    """Debug function to print users in a nice table format"""
    session = SessionLocal()
    try:
        users_db = session.query(UserDB).all()
        if not users_db:
            logger.info("No users found in database")
            return

        # Create PrettyTable and set headers
        table = PrettyTable()
        table.field_names = [
            "ID",
            "Name",
            "Lastname",
            "Age",
            "Email",
            "Phone",
            "Membership",
            "Renovation",
            "Created At",
        ]

        # Add rows to table
        for user in users_db:
            table.add_row(
                [
                    user.id,
                    user.name,
                    user.lastname,
                    user.age,
                    user.email,
                    user.phone,
                    user.membership_type,
                    user.renovation_date,
                    user.created_at,
                ]
            )

        # Set alignment and style
        table.align = "l"  # Left align text
        table.border = True
        table.header = True

        # Print table
        print("\nUsers in database:")
        print(table)
    except SQLAlchemyError as e:
        logger.error(f"Error getting users: {str(e)}")
    finally:
        session.close()


# ----- Funciones de Entrenador (Trainer) -----


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


def get_trainer(unique_id):
    """Gets a trainer by their ID"""
    session = SessionLocal()
    try:
        trainer_db = session.query(TrainerDB).filter(TrainerDB.id == unique_id).first()
        if trainer_db:
            return db_to_trainer(trainer_db)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error getting trainer: {str(e)}")
        return None
    finally:
        session.close()


def get_all_trainers():
    """Gets all trainers"""
    session = SessionLocal()
    try:
        trainers_db = session.query(TrainerDB).all()
        return [db_to_trainer(trainer_db) for trainer_db in trainers_db]
    except SQLAlchemyError as e:
        logger.error(f"Error getting trainers: {str(e)}")
        return []
    finally:
        session.close()


def update_trainer(trainer):
    """Updates an existing trainer"""
    if not trainer.unique_id:
        logger.error("Cannot update a trainer without an ID")
        return False

    session = SessionLocal()
    try:
        trainer_db = (
            session.query(TrainerDB).filter(TrainerDB.id == trainer.unique_id).first()
        )
        if not trainer_db:
            logger.warning(f"Trainer with ID {trainer.unique_id} not found")
            return False

        trainer_db.name = trainer.name
        trainer_db.age = trainer.age
        trainer_db.email = trainer.email
        trainer_db.phone = trainer.phone
        trainer_db.specialty = trainer.specialty
        trainer_db.start_time = trainer.start_time
        trainer_db.end_time = trainer.end_time

        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating trainer: {str(e)}")
        return False
    finally:
        session.close()


def delete_trainer(unique_id):
    """Deletes a trainer by their ID"""
    session = SessionLocal()
    try:
        trainer_db = session.query(TrainerDB).filter(TrainerDB.id == unique_id).first()
        if not trainer_db:
            logger.warning(f"Trainer with ID {unique_id} not found")
            return False

        session.delete(trainer_db)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error deleting trainer: {str(e)}")
        return False
    finally:
        session.close()


def link_trainer_to_admin(trainer_id, admin_username):
    """Links a trainer to an admin account (manager role)"""
    session = SessionLocal()
    try:
        trainer_db = session.query(TrainerDB).filter(TrainerDB.id == trainer_id).first()
        admin_db = (
            session.query(AdminDB).filter(AdminDB.username == admin_username).first()
        )

        if not trainer_db or not admin_db:
            return False

        if getattr(admin_db, "role", None) != AdminRoles.MANAGER:
            admin_db.role = AdminRoles.MANAGER

        trainer_db.admin_username = admin_username

        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error linking trainer to admin: {str(e)}")
        return False
    finally:
        session.close()


def debug_print_trainers():
    """Debug function to print trainers in a nice table format"""
    session = SessionLocal()
    try:
        trainers_db = session.query(TrainerDB).all()
        if not trainers_db:
            logger.info("No trainers found in database")
            return

        # Create PrettyTable and set headers
        table = PrettyTable()
        table.field_names = [
            "ID",
            "Name",
            "Lastname",
            "Age",
            "Email",
            "Phone",
            "Specialty",
            "Start Time",
            "End Time",
            "Created At",
            "Admin Username"
        ]

        # Add rows to table
        for trainer in trainers_db:
            table.add_row(
                [
                    trainer.id,
                    trainer.name,
                    trainer.lastname,
                    trainer.age,
                    trainer.email,
                    trainer.phone,
                    trainer.specialty,
                    trainer.start_time,
                    trainer.end_time,
                    trainer.created_at,
                    trainer.admin_username
                ]
            )

        # Set alignment and style
        table.align = "l"  # Left align text
        table.border = True
        table.header = True

        # Print table
        print("\nTrainers in database:")
        print(table)
    except SQLAlchemyError as e:
        logger.error(f"Error getting trainers: {str(e)}")
    finally:
        session.close()


# ----- Funciones de Administrador (Admin) -----


def create_admin(admin):
    """Creates a new admin in the database"""
    session = SessionLocal()
    try:
        # Reuse the helper function
        if _check_admin_username_exists(session, admin.username):
            logger.warning(f"Admin with username '{admin.username}' already exists")
            return None

        admin_db = admin_to_db(admin)
        session.add(admin_db)
        session.commit()
        admin.unique_id = admin_db.id
        return admin
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error creating admin: {str(e)}")
        return None
    finally:
        session.close()


def get_admin(username):
    """Gets an admin by their username"""
    session = SessionLocal()
    try:
        admin_db = session.query(AdminDB).filter(AdminDB.username == username).first()
        if admin_db:
            return db_to_admin(admin_db)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error getting admin: {str(e)}")
        return None
    finally:
        session.close()


def get_all_admins():
    """Gets all admins"""
    session = SessionLocal()
    try:
        admins_db = session.query(AdminDB).all()
        return [db_to_admin(admin_db) for admin_db in admins_db]
    except SQLAlchemyError as e:
        logger.error(f"Error getting admins: {str(e)}")
        return []
    finally:
        session.close()


def update_admin(admin):
    """Updates an existing admin"""
    if not admin.unique_id:
        logger.error("Cannot update an admin without an ID")
        return False

    session = SessionLocal()
    try:
        admin_db = session.query(AdminDB).filter(AdminDB.id == admin.unique_id).first()
        if not admin_db:
            logger.warning(f"Admin with ID {admin.unique_id} not found")
            return False

        # Update username
        admin_db.username = admin.username

        # Only update password if a new one was provided
        # admin.password will contain the new hashed password, or None if not changed
        if hasattr(admin, '_password') and admin._password is not None:
            admin_db.password_hash = admin._password

        # Update role
        admin_db.role = admin.role

        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error updating admin: {str(e)}")
        return False
    finally:
        session.close()


def delete_admin(requester_admin, admin_id_to_delete):
    """
    Elimina un admin por su ID.
    Solo admins pueden eliminar admins.
    """
    if not has_admin_permission(requester_admin, AdminRoles.ADMIN):
        logger.warning(f"Unauthorized delete attempt by {requester_admin.username}")
        return False

    session = SessionLocal()
    try:
        admin_db = (
            session.query(AdminDB).filter(AdminDB.id == admin_id_to_delete).first()
        )
        if not admin_db:
            return False

        if is_last_admin(session):
            logger.warning("Cannot delete the last admin")
            return False

        session.delete(admin_db)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error deleting admin: {str(e)}")
        return False
    finally:
        session.close()


def debug_print_admins():
    """Debug function to print admins in a nice table format"""
    session = SessionLocal()
    try:
        admins_db = session.query(AdminDB).all()
        if not admins_db:
            logger.info("No admins found in database")
            return

        # Create PrettyTable and set headers
        table = PrettyTable()
        table.field_names = ["ID", "Username", "Role", "Created At"]

        # Add rows to table
        for admin in admins_db:
            table.add_row(
                [
                    admin.id,
                    admin.username,
                    admin.role,
                    admin.created_at,
                ]
            )

        # Set alignment and style
        table.align = "l"  # Left align text
        table.border = True
        table.header = True

        # Print table
        print("\nAdmins in database:")
        print(table)
    except SQLAlchemyError as e:
        logger.error(f"Error getting admins: {str(e)}")
    finally:
        session.close()


def is_admin_username_available(username):
    """Public API to check if username is available"""
    session = SessionLocal()
    try:
        return not _check_admin_username_exists(session, username)
    except SQLAlchemyError as e:
        logger.error(f"Error checking username: {str(e)}")
        return False
    finally:
        session.close()


def is_last_admin(session):
    """Checks if there is only one admin in the database"""
    admin_count = session.query(AdminDB).count()
    return admin_count == 1


def ensure_default_admin_exists():
    """Ensures that there is at least one admin in the system"""
    session = SessionLocal()
    try:
        admin_count = session.query(AdminDB).count()
        if admin_count == 0:

            default_admin = Admin(
                username=DEFAULT_ADMIN["username"],
                password=DEFAULT_ADMIN["password"],
                role=DEFAULT_ADMIN["role"],
            )

            create_admin(default_admin)
            logger.info("Created default admin account")

    except SQLAlchemyError as e:
        logger.error(f"Error ensuring default admin: {str(e)}")
    finally:
        session.close()


def authenticate_admin(username, password):
    """Authenticates an admin by username and password"""
    admin = get_admin(username)
    if admin and admin.verify_password(password):
        return admin
    return None


def is_admin(username):
    """Checks if a given username belongs to an admin account

    Args:
        username (str): The username to check

    Returns:
        bool: True if the username belongs to an admin account, False otherwise
    """
    session = SessionLocal()
    try:
        admin_db = session.query(AdminDB).filter(AdminDB.username == username).first()
        return admin_db is not None
    except SQLAlchemyError as e:
        logger.error(f"Error checking admin status: {str(e)}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    # 1. Create a test admin
    test_admin = Admin(
        username="test_admin",
        password="test123",
        role=AdminRoles.ADMIN
    )

    print("\n=== Test for admin creation and authentication ===")
    print(f"Creating admin with username: {test_admin.username}")

    # 2. Store it in the database
    created_admin = create_admin(test_admin)
    if created_admin:
        print("✅ Admin successfully created")
    else:
        print("❌ Error creating admin")
        exit(1)

    # 3. Attempt to retrieve the admin
    retrieved_admin = get_admin("test_admin")
    if retrieved_admin:
        print("✅ Admin successfully retrieved")
    else:
        print("❌ Error retrieving admin")
        exit(1)

    # 4. Test authentication with correct password
    print("\nTesting authentication with correct credentials:")
    auth_result = authenticate_admin("test_admin", "test123")
    print(f"Result: {'✅ Successful' if auth_result else '❌ Failed'}")

    # 5. Test authentication with incorrect password
    print("\nTesting authentication with incorrect credentials:")
    wrong_auth = authenticate_admin("test_admin", "wrong_password")
    print(f"Result: {'❌ Correct' if not wrong_auth else '⚠️ Incorrect'}")

    # 6. Display all admins in the database
    print("\nFinal state of the database:")
    debug_print_admins()
