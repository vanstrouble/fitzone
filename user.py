from person import Person


class User(Person):
    def __init__(
        self, name=None, age=None, email=None, phone=None,
        membership_type=None, created_at=None
    ):
        super().__init__(name, age, email, phone, created_at)
        self._unique_id = None
        self._membership_type = membership_type

    def __str__(self):
        return f'''
            ID: {self._unique_id}
            {super().__str__().strip()}
            Membership Type: {self._membership_type}
        '''

    @property
    def unique_id(self):
        return self._unique_id

    @unique_id.setter
    def unique_id(self, unique_id):
        if self._unique_id is None:
            self._unique_id = unique_id

    @property
    def membership_type(self):
        return self._membership_type

    @membership_type.setter
    def membership_type(self, membership_type):
        self._membership_type = membership_type

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "membership_type": self._membership_type
        })
        return base_dict


if __name__ == "__main__":
    user_test = User("Antonio", 26, "email@email.com", "1234567890", "monthly")
    print(user_test.__str__())
    print(user_test.to_dict())
