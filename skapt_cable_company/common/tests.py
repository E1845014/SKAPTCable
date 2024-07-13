"""
Module for all Common Models Tests
"""

# pylint: disable=imported-auth-user

from time import time
from typing import List, Union
from random import choices, choice
from string import ascii_letters

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Employee, Area


class EmployeeTestCase(TestCase):
    """
    Test cases to test Employee Model
    """

    def test_str(self):
        """
        Test Employee Models String
        """
        user = User.objects.create_user("username", "email@email.com", "password")
        user.first_name = "first_name"
        user.last_name = "last_name"
        user.save()

        employee = Employee.objects.create(user=user, phone_number="0777777777")
        self.assertEqual(
            str(employee),
            f"{user.first_name} {user.last_name}",
        )


class BaseTestCase(TestCase):
    """
    Test Case Funcationalites Common for All App Test Cases
    """

    def setUp(self):
        """
        Runs on Test Case Start up

        Contains Base Data needed for testing
        """
        self.raw_password = "top_secret"
        self.super_user = User.objects.create_superuser(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def get_random_phone_number(self):
        """
        Generate Random Phone Number within the Regex Validation
        """
        return f"07{str(int(time()*100))[-8:]}"

    def get_random_string(self, n=5):
        """
        Generate n length random string
        """
        return "".join(choices(ascii_letters, k=n))

    def generate_employees(self, n=5):
        """
        Generate n Number of Employees
        """
        employees: List[Employee] = []
        for i in range(n):
            user = User.objects.create_user(
                username=f"{int(time())}{i}",
                email=f"{int(time())}@{i}xz.com",
                password=self.raw_password,
            )
            user.save()
            employee = Employee.objects.create(
                user=user, phone_number=self.get_random_phone_number()
            )
            employees.append(employee)
        return employees

    def generate_areas(self, n=5, employees: Union[None, List[Employee]] = None):
        """
        Generate n Number of Areas
        """
        if employees is None:
            employees = self.generate_employees()
        areas: List[Area] = []
        for _ in range(n):
            areas.append(
                Area.objects.create(
                    name=self.get_random_string(), agent=choice(employees)
                )
            )
        return areas

    def login_as_employee(self, employee: Employee, make_admin=False):
        """
        Login Client as an employee
        """
        if make_admin:
            employee.is_admin = True
            employee.save()
        return self.client.login(
            username=employee.user.username, password=self.raw_password
        )

    def login_as_superuser(self):
        """
        Login Client as super user
        """
        return self.client.login(
            username=self.super_user.username, password=self.raw_password
        )
