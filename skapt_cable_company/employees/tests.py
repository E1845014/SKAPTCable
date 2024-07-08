"""
Module for all the Employees Related Test Cases
"""

# pylint: disable=imported-auth-user

from django.test import TestCase
from django.contrib.auth.models import User
from django.forms import Form

from time import time
from typing import List

from common.models import Employee


class EmployeeBaseTestCase(TestCase):
    """
    Base Test Functionalities for Employee App Testings
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

    def generate_employees(self, n=5):
        """
        Generate n Number of Employees
        """
        employees: List[Employee] = []
        for i in range(n):
            user = User.objects.create_user(
                username=f"{time()}{i}",
                email=f"{time()}@{i}.com",
                password=self.raw_password,
            )
            user.is_staff = True
            user.save()
            employee = Employee.objects.create(
                user=user, phone_number=self.get_random_phone_number()
            )
            employees.append(employee)
        return employees

    def login_as_employee(self, employee: Employee):
        """
        Login Client as an employee
        """
        return self.client.login(
            username=employee.user.username, password=self.raw_password
        )


class EmployeesTestCase(EmployeeBaseTestCase):
    """
    Test Cases for testing Employees List Page and their functionality
    """

    def test_page_renders_for_employees(self):
        """
        Test if the employees page renders for employee user
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get("/employees/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("employees.html")
        self.client.logout()
        response = self.client.get("/employees/")
        self.assertNotEqual(response.status_code, 200)

    def test_shows_all_employees(self):
        """
        Test if all the employees are shown
        """
        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        response = self.client.get("/employees/")
        self.assertEqual(len(response.context["employees"]), len(employees))


class AddEmployeeTestCase(EmployeeBaseTestCase):
    """
    Test Cases for testing Add new Employee Functionality and UI
    """

    def test_page_renders_for_employees(self):
        """
        Test if the page only loads for employees and super admins
        """
        employee = self.generate_employees(1)[0]
        non_employee_user = User.objects.create_user(
            "username", "email@mail.co", self.raw_password
        )
        self.login_as_employee(employee)
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(
            username=non_employee_user.username, passsword=self.raw_password
        )
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 302)
        self.client.login(username=self.super_user.username, password=self.raw_password)
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 200)

    def test_form_fields(self):
        """
        Test the fields passed in the form
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get("/employees/add")
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]
        expected_user_form_fields = ["first_name", "last_name", "email"]
        for expected_user_form_field in expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("employee_form", response.context)
        employee_form: Form = response.context["employee_form"]
        expected_employee_form_fields = ["phone_number", "is_admin"]
        for expected_employee_form_field in expected_employee_form_fields:
            self.assertIn(expected_employee_form_field, employee_form.fields)
        self.assertTemplateUsed("add_employees.html")
