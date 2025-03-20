from person import Person


class User(Person):
    def __init__(self, id_user=None, name=None, age=None, email=None, phone=None, membership_type=None):
        super().__init__(name, age, email, phone)
        self._id_user = id_user
        self._membership_type = membership_type

    def __str__(self):
        return f'''
            ID: {self._id_user}
            {super().__str__().strip()}
            Membership Type: {self._membership_type}
        '''

    @property
    def id_user(self):
        return self._id_user

    @id_user.setter
    def id_user(self, id_user):
        self._id_user = id_user

    @property
    def membership_type(self):
        return self._membership_type

    @membership_type.setter
    def membership_type(self, membership_type):
        self._membership_type = membership_type

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "id_user": self._id_user,
            "membership_type": self._membership_type
        })
        return base_dict


if __name__ == "__main__":
    user_test = User(1, "Antonio", 26, "email@email.com", "1234567890", "monthly")
    print(user_test.__str__())
    print(user_test.to_dict())
