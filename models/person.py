from datetime import datetime


class Person:
    def __init__(self, name=None, lastname=None, age=None, email=None, phone=None, created_at=None):
        self._name = name
        self._lastname = lastname
        self._age = age
        self._email = email
        self._phone = phone
        self._created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:00")

    def __str__(self):
        return f'''
            Name: {self._name}
            Lastname: {self._lastname}
            Age: {self._age}
            Email: {self._email}
            Phone: {self._phone}
            Created At: {self._created_at}
        '''

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def lastname(self):
        return self._lastname

    @lastname.setter
    def lastname(self, lastname):
        self._lastname = lastname

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age):
        self._age = age

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, email):
        self._email = email

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, phone):
        self._phone = phone

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
            "name": self._name,
            "lastname": self._lastname,
            "age": self._age,
            "email": self._email,
            "phone": self._phone,
            "created_at": self._created_at
        }


if __name__ == "__main__":
    person_test = Person(
        "Antonio", "Vázquez", 26, "email@email.com", "1234567890", "2021-09-01 14:00"
    )
    print(person_test.__str__())
    print(person_test.to_dict())
