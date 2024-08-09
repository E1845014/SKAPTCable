"""
Module for all the Employees Related Test Cases
"""

# pylint: disable=imported-auth-user

from django.contrib.auth.models import User
from django.forms import Form


from common.models import Employee
from common.tests import BaseTestCase


class EmployeeBaseTestCase(BaseTestCase):
    """
    Base Test Functionalities for Employee App Testings
    """


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

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the employee page not renders for non-employees
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.get("/employees/")
        self.assertEqual(response.status_code, 403)

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
        Test if the page only loads for employees
        """
        employee = self.generate_employees(1)[0]

        self.login_as_employee(employee)
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_page_not_renders_for_non_employee(self):
        """
        Test if the page not loads for non employees
        """
        self.login_as_non_employee()
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 403)

    def test_page_renders_for_superuser(self):
        """
        Test if the page only loads for super user
        """
        self.login_as_superuser()
        response = self.client.get("/employees/add")
        self.assertEqual(response.status_code, 200)

    def test_form_fields(self):
        """
        Test the fields passed in the form
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee, True)
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
        employee.is_admin = True
        employee.save()
        self.login_as_employee(employee)
        request_object = {}
        new_employee_phone_number = self.get_random_phone_number()
        for field in (
            self.expected_employee_form_fields + self.expected_user_form_fields
        ):
            if field == "email":
                request_object[field] = "email@email.com"
            elif field == "phone_number":
                request_object[field] = new_employee_phone_number
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

    def test_form_submission_as_non_employee(self):
        """
        Test the form submission on correct variables
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        request_object = {}
        new_employee_phone_number = self.get_random_phone_number()
        for field in (
            self.expected_employee_form_fields + self.expected_user_form_fields
        ):
            if field == "email":
                request_object[field] = "email@email.com"
            elif field == "phone_number":
                request_object[field] = new_employee_phone_number
            else:
                request_object[field] = field
        response = self.client.post("/employees/add", request_object)
        self.assertEqual(response.status_code, 403)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

    def test_make_super_admin_by_non_admin_employee(self):
        """
        Test whether non admin employee cannot make someone as admin
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_object = {}
        new_employee_phone_number = self.get_random_phone_number()
        for field in (
            self.expected_employee_form_fields + self.expected_user_form_fields
        ):
            if field == "email":
                request_object[field] = "email@email.com"
            elif field == "phone_number":
                request_object[field] = new_employee_phone_number
            else:
                request_object[field] = field
        request_object["is_admin"] = True
        response = self.client.post("/employees/add", request_object)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        new_employee = new_employee_query[0]
        self.assertFalse(new_employee.is_admin)
        self.assertEqual(response.status_code, 302)

    def test_wrong_request_type(self):
        """
        Test whether other request types are supported
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.put("/employees/add")
        self.assertEqual(response.status_code, 400)

    def test_errored_form_submission(self):
        """
        Test the form submission on incorrect variables
        """
        employee = self.generate_employees(1)[0]
        employee.is_admin = True
        employee.save()
        self.login_as_employee(employee)
        request_object = {}
        new_employee_phone_number = self.get_random_phone_number()
        for field in (
            self.expected_employee_form_fields + self.expected_user_form_fields
        ):
            if field == "email":
                request_object[field] = "email"
            elif field == "phone_number":
                request_object[field] = new_employee_phone_number
            else:
                request_object[field] = field
        response = self.client.post("/employees/add", request_object)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertEqual(len(new_employee_query), 0)
        self.assertEqual(response.status_code, 200)


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
        self.login_as_employee(employees[0],True)
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

    def test_non_employee_page_not_renders(self):
        """
        Test if the page not renders for non-employees for any employee
        """
        employees = self.generate_employees()
        new_user = User.objects.create_user(
            "username", "email@email.com", self.raw_password
        )
        self.client.login(username=new_user.username, password=self.raw_password)
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
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]

        for expected_user_form_field in expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("employee_form", response.context)
        employee_form: Form = response.context["employee_form"]

        for expected_employee_form_field in expected_employee_form_fields:
            self.assertIn(expected_employee_form_field, employee_form.fields)

    def test_not_exist_employee(self):
        """
        Test whether page handles not existing employee search
        """
        employees = self.generate_employees()
        self.login_as_employee(employees[0])
        unexist_phone_number = self.get_random_phone_number()
        response = self.client.get(f"/employees/{unexist_phone_number}")
        self.assertEqual(response.status_code, 404)


class UpdateEmployeeTestCase(EmployeeBaseTestCase):
    """
    Testcase for Update Employee UI and Functionality
    """

    def test_page_renders(self):
        """
        Test if the page renders
        """
        employees = self.generate_employees()
        self.login_as_superuser()
        response = self.client.get(f"/employees/{employees[0].user.username}/update")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_employee.html")

    def test_non_employee_page_not_renders(self):
        """
        Test if the page not renders for non-employees for any employee
        """
        employees = self.generate_employees()
        new_user = User.objects.create_user(
            "username", "email@email.com", self.raw_password
        )
        self.client.login(username=new_user.username, password=self.raw_password)
        response = self.client.get(f"/employees/{employees[1].user.username}")
        self.assertEqual(response.status_code, 403)

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
        """
        Test whether super user can update employee
        """
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
        """
        Test whether Admin Employee can update employee
        """
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
        """
        Test whether employee can update themself
        """
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
        """
        Test whether non-admin Employees can't update other employees
        """
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

    def test_for_non_employee(self):
        """
        Test the form submission as non employee failing
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)

        employees = self.generate_employees()

        ## Test for Non Employee Page Renders
        response = self.client.get(f"/employees/{employees[1].user.username}/update")
        self.assertEqual(response.status_code, 403)

        ## Retrieve user form details
        self.login_as_employee(employees[1])
        response = self.client.get(f"/employees/{employees[1].user.username}/update")
        request_object = {}
        new_employee_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        employee_form: Form = response.context["employee_form"]
        request_object = {**user_form.initial, **employee_form.initial}
        request_object["phone_number"] = new_employee_phone_number

        ## Test for Non Employee Form Submission
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.post(
            f"/employees/{employees[1].user.username}/update", request_object
        )
        self.assertEqual(response.status_code, 403)
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

    def test_invalid_data(self):
        """
        Test whether invalid data is handled
        """
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
        """
        Test whether duplicate phone number is handled
        """
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
        self.assertIn(
            "Employee with this Phone number already exists.",
            employee_form.errors["phone_number"],
        )
        new_employee_query = Employee.objects.filter(
            phone_number=employees[1].phone_number
        )
        self.assertTrue(len(new_employee_query) == 1)

    def test_make_super_admin_by_non_admin_employee(self):
        """
        Test whether non admin employee cannot make someone as admin
        """
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
        request_object["is_admin"] = True
        response = self.client.post(
            f"/employees/{employee.user.username}/update", request_object
        )
        new_employee_query = Employee.objects.filter(
            phone_number=new_employee_phone_number
        )
        self.assertTrue(len(new_employee_query) > 0)
        new_employee = new_employee_query[0]
        self.assertFalse(new_employee.is_admin)
        self.assertEqual(response.status_code, 302)
