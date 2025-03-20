class Person:
    def __init__(self, name=None, age=None, email=None, phone=None):
        self._name = name
        self._age = age
        self._email = email
        self._phone = phone

    def __str__(self):
        return f'''
            Name: {self._name}
            Age: {self._age}
            Email: {self._email}
            Phone: {self._phone}
        '''

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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

    def to_dict(self):
        return {
            "name": self._name,
            "age": self._age,
            "email": self._email,
            "phone": self._phone,
        }


if __name__ == "__main__":
    person_test = Person("Antonio", 26, "email@email.com", "1234567890")
    print(person_test.__str__())
    print(person_test.to_dict())
