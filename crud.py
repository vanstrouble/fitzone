from database import SessionLocal
from models import User
from prettytable import PrettyTable


def create_user(name, age, email, phone, membership_type):
    session = SessionLocal()
    try:
        new_user = User(
            name=name,
            age=age,
            email=email,
            phone=phone,
            membership_type=membership_type
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except Exception as e:
        print(f"Error al insertar usuario: {e}")
        session.rollback()
    finally:
        session.close()


def get_all_users():
    session = SessionLocal()
    try:
        users = session.query(User).all()

        if not users:
            print("🔴 No hay usuarios registrados.")
            return

        table = PrettyTable()
        table.field_names = ["ID", "Nombre", "Edad", "Email", "Teléfono", "Membresía", "Registro"]

        for user in users:
            table.add_row([
                user.id, user.name, user.age, user.email,
                user.phone, user.membership_type, user.created_at
            ])

        print(table)
    finally:
        session.close()


if __name__ == "__main__":
    get_all_users()
