class User:
    def __init__(self, id_user=None, name=None, age=None, email=None, phone=None, membership_type= None):
        self._id_user = id_user
        self._name = name
        self._age = age
        self._email = email
        self._phone = phone
        self._membership_type = membership_type

    def __str__(self):
        return f'''
            ID: {self._id_user}
            Name: {self._name}
            Age: {self._age}
            Email: {self._email}
            Phone: {self._phone}
            Membership Type: {self._membership_type}
        '''

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, id_user):
        self._id_user = id_user

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

    @property
    def membership_type(self):
        return self._membership_type

    @membership_type.setter
    def membership_type(self, membership_type):
        self._membership_type = membership_type

    def to_dict(self):
        return {
            "id_user": self._id_user,
            "name": self._name,
            "age": self._age,
            "email": self._email,
            "phone": self._phone,
            "membership_type": self._membership_type
        }


if __name__ == "__main__":
    user_test = User(1, "Antonio", 26, "email@email.com", "1234567890", "monthly")
    print(user_test.__str__())
    print(user_test.to_dict())
