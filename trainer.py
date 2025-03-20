from user import User


class Trainer(User):
    def __init__(self, id_user=None, name=None, age=None, email=None, phone=None, specialty=None, start_time=None, end_time=None):
        super().__init__(id_user, name, age, email, phone)
        self._specialty = specialty
        self._start_time = start_time
        self._end_time = end_time

    def __str__(self):
        return f'''
            ID: {self.id_user}
            Name: {self.name}
            Age: {self.age}
            Email: {self.email}
            Phone: {self.phone}
            Specialty: {self._specialty}
            Start Time: {self._start_time}
            End Time: {self._end_time}
        '''

    @property
    def specialty(self):
        return self._specialty

    @specialty.setter
    def specialty(self, specialty):
        self._specialty = specialty

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        self._start_time = start_time

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        self._end_time = end_time

    def to_dict(self):
        return {
            "id_user": self.id_user,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "phone": self.phone,
            "specialty": self._specialty,
            "start_time": self._start_time,
            "end_time": self._end_time,
        }


if __name__ == "__main__":
    trainer_test = Trainer(
        1, "Antonio", 26, "email@email.com", "1234567890", "Crossfit", "08:00", "16:00"
    )
    print(trainer_test.__str__())
    print(trainer_test.to_dict())
