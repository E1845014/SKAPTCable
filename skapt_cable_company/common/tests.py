from django.contrib.auth.models import User
from django.test import TestCase

from .models import Employee


class EmployeeTestCase(TestCase):
    """
    Test cases to test Employee Model
    """

    def test_str(self):
        user = User.objects.create_user("username", "email@email.com", "password")
        user.first_name = "first_name"
        user.last_name = "last_name"
        user.save()

        employee = Employee.objects.create(user=user, phone_number="0777777777")
        self.assertEqual(
            str(employee),
            f"{str(user)} {user.first_name} {user.last_name}",
        )
