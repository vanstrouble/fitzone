from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# Create a global instance with secure but balanced configuration
ph = PasswordHasher(
    time_cost=2,  # Number of iterations (2-4 is a good balance)
    memory_cost=19456,  # Memory in KiB (64MB is reasonable for desktop applications)
    parallelism=2,  # Number of parallel threads
    hash_len=32,  # Length of the resulting hash
    salt_len=16,  # Length of the salt
)


class Admin:
    def __init__(self, username=None, password=None, role=None, created_at=None):
        self._unique_id = None
        self._username = username
        self._password = None
        self._role = role
        self._created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:00")

        if password:
            self.set_password(password)

    def __str__(self):
        return f"""
            ID: {self._unique_id}
            Username: {self._username}
            role: {self._role}
            Created At: {self._created_at}
        """

    @property
    def unique_id(self):
        return self._unique_id

    @unique_id.setter
    def unique_id(self, unique_id):
        if self._unique_id is None:
            self._unique_id = unique_id

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    def set_password(self, password):
        """Stores the password using Argon2 hashing"""
        if password:
            try:
                self._password = ph.hash(password)
            except Exception as e:
                raise ValueError(f"Error hashing the password: {e}")
        else:
            self._password = None

    def verify_password(self, password):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        if not password or not self._password:
            return False

        try:
            return ph.verify(self._password, password)
        except VerifyMismatchError:
            return False
        except Exception:
            return False

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        self.set_password(password)

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        try:
            datetime.strptime(created_at, "%Y-%m-%d %H:00")
            self._created_at = created_at
        except ValueError:
            raise ValueError("created_at must be in the format 'YYYY-MM-DD HH:00'")

    def to_dict(self):
        return {
            "username": self._username,
            "password": self._password,
            "role": self._role,
            "created_at": self._created_at,
        }


if __name__ == "__main__":
    admin = Admin("admin", "password", "admin")
    print(admin)
    print(admin.to_dict())

    # Correct verification
    print(f"Correct verification: {admin.verify_password('password')}")

    # Incorrect verification
    print(f"Incorrect verification: {admin.verify_password('wrong_password')}")
