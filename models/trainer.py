import re
from models.user import User


class Trainer(User):
    def __init__(
        self,
        name=None,
        lastname=None,
        age=None,
        email=None,
        phone=None,
        specialty=None,
        start_time=None,
        end_time=None,
        created_at=None,
    ):
        super().__init__(name, lastname, age, email, phone, created_at)
        self._unique_id = None
        self._specialty = specialty
        self._start_time = start_time
        self._end_time = end_time

    def __str__(self):
        return f'''
            ID: {self.unique_id}
            Name: {self.name}
            Lastname: {self.lastname}
            Age: {self.age}
            Email: {self.email}
            Phone: {self.phone}
            Specialty: {self._specialty}
            Start Time: {self._start_time}
            End Time: {self._end_time}
            Created At: {self.created_at}
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
        if start_time and not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', start_time):
            raise ValueError("The time format must be HH:MM (24h)")
        self._start_time = start_time

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        if end_time and not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', end_time):
            raise ValueError("The time format must be HH:MM (24h)")
        self._end_time = end_time

    def to_dict(self):
        return {
            "name": self.name,
            "lastname": self.lastname,
            "age": self.age,
            "email": self.email,
            "phone": self.phone,
            "specialty": self._specialty,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "created_at": self.created_at,
        }


if __name__ == "__main__":
    trainer_test = Trainer(
        "Antonio", "Vázquez", 26, "email@email.com", "1234567890", "Crossfit", "08:00", "16:00"
    )
    print(trainer_test.__str__())
    print(trainer_test.to_dict())
