from datetime import datetime
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Admin:
    def __init__(self, username=None, password=None, role=None, created_at=None):
        self._unique_id = None
        self._username = username
        self._password = password
        self.set_password(password)
        self._role = role
        self._created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:00")

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
        """Encrypts and stores the password"""
        if password:
            self._password = pwd_context.hash(password)

    def verify_password(self, plain_password):
        """Verifies if the provided password matches the hash"""
        if not plain_password or not self._password:
            return False
        return pwd_context.verify(plain_password, self._password)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

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
            "created_at": self._created_at,
        }


if __name__ == "__main__":
    admin = Admin("admin", "password", "superuser")
    print(admin)
    print(admin.to_dict())
