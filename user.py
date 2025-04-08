import re
from person import Person
from datetime import datetime, timedelta


class User(Person):
    def __init__(
        self,
        name=None,
        lastname=None,
        age=None,
        email=None,
        phone=None,
        membership_type=None,
        created_at=None,
        renovation_date=None,
    ):
        super().__init__(name, lastname, age, email, phone, created_at)
        self._unique_id = None
        self._membership_type = membership_type
        self.renovation_date = renovation_date

    def __str__(self):
        return f"""
            ID: {self._unique_id}
            {super().__str__().strip()}
            Membership Type: {self._membership_type}
            Renovation Date: {self._renovation_date}
        """

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

    @property
    def renovation_date(self):
        return self._renovation_date

    @renovation_date.setter
    def renovation_date(self, renovation_date):
        if renovation_date is None:
            # If no date provided, set to next month same day and hour
            current = datetime.strptime(self.created_at, "%Y-%m-%d %H:00")
            next_month = current + timedelta(days=30)
            self._renovation_date = next_month.strftime("%Y-%m-%d %H:00")
        else:
            # Validate format YYYY-MM-DD HH:00
            if not re.match(
                r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]) "
                r"(?:[01]\d|2[0-3]):00$",
                renovation_date,
            ):
                raise ValueError("Renovation date must be in format 'YYYY-MM-DD HH:00'")

            # Validate that renovation date is after creation date
            renovation = datetime.strptime(renovation_date, "%Y-%m-%d %H:00")
            creation = datetime.strptime(self.created_at, "%Y-%m-%d %H:00")

            if renovation <= creation:
                raise ValueError("Renovation date must be after creation date")

            self._renovation_date = renovation_date

    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update(
            {
                "membership_type": self._membership_type,
                "renovation_date": self._renovation_date,
            }
        )
        return base_dict


if __name__ == "__main__":
    user_test_1 = User(
        "Antonio", "Vázquez", 26, "email@email.com", "1234567890", "monthly"
    )
    user_test_2 = User(
        "Aideé",
        "Correa",
        27,
        "email@email.com",
        "1234567890",
        "anual",
        "2026-10-01 14:00",
    )

    print(user_test_1.__str__())
    print(user_test_1.to_dict())
    print(user_test_2.__str__())
    print(user_test_2.to_dict())
