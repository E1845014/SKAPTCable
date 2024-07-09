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
                username=f"{int(time())}{i}",
                email=f"{int(time())}@{i}xz.com",
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

    def login_as_superuser(self):
        """
        Login Client as super user
        """
        return self.client.login(
            username=self.super_user.username, password=self.raw_password
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

    def setUp(self):
        """
        Setup Add Employee Testings
        """
        self.expected_user_form_fields = ["first_name", "last_name", "email"]
        self.expected_employee_form_fields = ["phone_number", "is_admin"]
        return super().setUp()

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
        self.login_as_superuser()
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

        for expected_user_form_field in self.expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("employee_form", response.context)
        employee_form: Form = response.context["employee_form"]

        for expected_employee_form_field in self.expected_employee_form_fields:
            self.assertIn(expected_employee_form_field, employee_form.fields)
        self.assertTemplateUsed("add_employees.html")

    def test_form_submission(self):
        """
        Test the form submission on correct variables
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_object = {}
        new_employee_phone_number = "0771234458"
        for field in (
            self.expected_employee_form_fields + self.expected_user_form_fields
        ):
            if field == "email":
                request_object[field] = "email@email.com"
            elif field == "phone_number":
                request_object[field] = "0771234458"
            else:
                request_object[field] = field
        response = self.client.post("/employees/add", request_object)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        new_employee = new_employee_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/employees/{new_employee.user.username}")


class ViewEmployeeTestCase(EmployeeBaseTestCase):
    """
    Test cases for view Employee Page view controller
    """

    def test_page_renders(self):
        """
        Test if the page renders and using correct template
        """
        employees = self.generate_employees()
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employees[0].user.username}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("employee.html")

    def test_self_page_renders(self):
        """
        Test if the page renders for employees to view their profile
        """
        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        response = self.client.get(f"/employees/{employees[0].user.username}")
        self.assertEqual(response.status_code, 200)

    def test_admin_page_renders(self):
        """
        Test if the page renders for admins to view other employees
        """
        employees = self.generate_employees()
        employees[0].is_admin = True
        employees[0].save()
        self.login_as_employee(employees[0])
        response = self.client.get(f"/employees/{employees[1].user.username}")
        self.assertEqual(response.status_code, 200)

    def test_non_admin_other_page_not_renders(self):
        """
        Test if the page not renders for non-admins to view other employees
        """
        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        response = self.client.get(f"/employees/{employees[1].user.username}")
        self.assertEqual(response.status_code, 403)

    def test_data_fields(self):
        """
        Test whether expected datas are passed
        """
        expected_user_form_fields = ["first_name", "last_name", "email"]
        expected_employee_form_fields = ["phone_number", "is_admin"]

        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        response = self.client.get(f"/employees/{employees[0].user.username}")
        user_form: Form = response.context["user_form"]

        for expected_user_form_field in expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("employee_form", response.context)
        employee_form: Form = response.context["employee_form"]

        for expected_employee_form_field in expected_employee_form_fields:
            self.assertIn(expected_employee_form_field, employee_form.fields)


class UpdateEmployeeTestCase(EmployeeBaseTestCase):
    """
    Testcase for Update Employee UI and Functionality
    """

    def test_page_renders(self):
        employees = self.generate_employees()
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employees[0].user.username}/update")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_employee.html")

    def test_has_correct_fields(self):
        """
        Test whether expected input fields are passed
        """
        expected_user_form_fields = ["first_name", "last_name", "email"]
        expected_employee_form_fields = ["phone_number", "is_admin"]

        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        response = self.client.get(f"/employees/{employees[0].user.username}/update")
        user_form: Form = response.context["user_form"]

        for expected_user_form_field in expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("employee_form", response.context)
        employee_form: Form = response.context["employee_form"]

        for expected_employee_form_field in expected_employee_form_fields:
            self.assertIn(expected_employee_form_field, employee_form.fields)

    def test_update_employee_as_super_user(self):
        employee = self.generate_employees(1)[0]
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employee.user.username}/update")
        request_object = {}
        new_employee_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number
        response = self.client.post(
            f"/employees/{employee.user.username}/update", request_object
        )
        self.assertEqual(response.status_code, 302)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        self.assertRedirects(
            response, f"/employees/{new_employee_query[0].user.username}"
        )

    def test_update_employee_as_admin(self):
        employees = self.generate_employees()
        employee = employees[0]
        employee.is_admin = True
        employee.save()
        self.login_as_employee(employee)
        response = self.client.get(f"/employees/{employees[1].user.username}/update")
        request_object = {}
        new_employee_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number
        response = self.client.post(
            f"/employees/{employees[1].user.username}/update", request_object
        )
        self.assertEqual(response.status_code, 302)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        self.assertRedirects(
            response, f"/employees/{new_employee_query[0].user.username}"
        )

    def test_update_employee_themself(self):
        employees = self.generate_employees()
        employee = employees[0]
        self.login_as_employee(employee)
        response = self.client.get(f"/employees/{employee.user.username}/update")
        request_object = {}
        new_employee_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number
        response = self.client.post(
            f"/employees/{employee.user.username}/update", request_object
        )
        self.assertEqual(response.status_code, 302)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        self.assertRedirects(
            response, f"/employees/{new_employee_query[0].user.username}"
        )

    def test_non_admin_employee_not_update_other_employee(self):
        employees = self.generate_employees()
        self.login_as_employee(employees[1])
        response = self.client.get(f"/employees/{employees[1].user.username}/update")
        request_object = {}
        new_employee_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number
        self.login_as_employee(employees[0])
        response = self.client.post(
            f"/employees/{employees[1].user.username}/update", request_object
        )
        self.assertEqual(response.status_code, 403)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

    def test_invalid_data(self):
        employee = self.generate_employees(1)[0]
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employee.user.username}/update")
        request_object = {}
        new_employee_phone_number = "0652223568"  ## Invalid Phone Number
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number
        response = self.client.post(
            f"/employees/{employee.user.username}/update", request_object
        )
        employee_form: Form = response.context["employee_form"]
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_employee.html")
        self.assertFalse(employee_form.is_valid())
        self.assertIn("Enter Valid Phone Number", employee_form.errors["phone_number"])
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

    def test_duplicate_phone_number(self):
        employees = self.generate_employees()
        employee = employees[0]
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employee.user.username}/update")
        request_object = {}
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = employees[1].phone_number
        response = self.client.post(
            f"/employees/{employee.user.username}/update", request_object
        )
        employee_form: Form = response.context["employee_form"]
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_employee.html")
        self.assertFalse(employee_form.is_valid())
        self.assertIn("Phone Number Already Exists", employee_form.errors["phone_number"])
        new_employee_query = Employee.objects.filter(
            phone_number=employees[1].phone_number
        )
        self.assertTrue(len(new_employee_query) == 1)
