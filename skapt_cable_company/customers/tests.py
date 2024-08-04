"""
Module to contain all Customers App View Controller Codes
"""

# pylint: disable=imported-auth-user

from django.contrib.auth.models import User
from django.forms import Form
from datetime import date

from common.tests import BaseTestCase
from common.models import Customer


class CustomerBaseTestCase(BaseTestCase):
    """
    Bese Tast Functionalities for Customer App Testing
    """


class CustomersTestCase(CustomerBaseTestCase):
    """
    Test Cases for testing Customers List Page and their functionalities
    """

    def test_page_renders_for_employees(self):
        """
        Test if the customers page renders for employee user
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("customers.html")
        self.client.logout()
        response = self.client.get("/customers/")
        self.assertNotEqual(response.status_code, 200)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the customers page not renders for non-employees
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 403)

    def test_shows_all_customers(self):
        """
        Test if all the employees are shown
        """
        customers = self.generate_customers()
        self.login_as_employee(customers[0].area.agent)
        response = self.client.get("/customers/")
        self.assertEqual(len(response.context["customers"]), len(customers))

    def test_other_request_method(self):
        """
        Test if the customers page not renders for any other request than GET
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.post("/customers/")
        self.assertNotEqual(response.status_code, 200)

    def test_customer_size(self):
        """
        Test if can filter customers based on the size of the list
        """
        self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_size = 1
        response = self.client.get("/customers/", {"size": request_size})
        self.assertEqual(len(response.context["customers"]), request_size)

    def test_page_number(self):
        """
        Test if can filter customers based on the page number
        """
        self.generate_customers(20)
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        page_number = 2
        response = self.client.get("/customers/", {"page": page_number})
        self.assertEqual(response.context["customers"].number, page_number)

    def test_non_numeric_params(self):
        """
        Test if can filter customers with wrong queries
        """
        self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_size = self.get_random_string()
        page_number = self.get_random_string()
        response = self.client.get(
            "/customers/", {"page": page_number, "size": request_size}
        )
        self.assertNotEqual(len(response.context["customers"]), request_size)
        self.assertNotEqual(response.context["customers"].number, page_number)

    def test_search_text(self):
        """
        Test if can filter customer with search text
        """
        customers = self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get(
            "/customers/", {"search_text": customers[0].identity_no}
        )
        self.assertEqual(response.context["customers"][0].pk, customers[0].pk)


class AddCustomerTestCase(CustomerBaseTestCase):

    def setUp(self):
        """
        Setup Add Area Testings
        """
        super().setUp()
        self.url = "/customers/add"
        self.expected_user_form_fields = ["first_name", "last_name", "email"]
        self.expected_form_fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "connection_start_date",
            "area",
        ]
        self.areas = self.generate_areas()

    def test_page_renders_for_admin_employees(self):
        """
        Test if the page loads for admin employees
        """
        employee = self.areas[0].agent
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_not_renders_for_non_admin_employees(self):
        """
        Test if the page not loads for non admin employees
        """
        employee = self.areas[0].agent
        self.login_as_employee(employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the page not renders for non employees
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_renders_for_superuser(self):
        """
        Test if the page renders for super users
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_form_fields(self):
        """
        Test the fields pased in the form
        """
        employee = self.areas[0].agent
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]
        for expected_user_form_field in self.expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("customer_form", response.context)
        customer_form: Form = response.context["customer_form"]

        for expected_customer_form_field in self.expected_form_fields:
            self.assertIn(expected_customer_form_field, customer_form.fields)
        self.assertTemplateUsed("add_employees.html")

    def test_post_request(self):
        """
        Test the form submission on correct variables
        """
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email@email.com"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_form_submission_as_non_employee(self):
        """
        Test the form submission on correct variables
        """
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email@email.com"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        self.client.logout()
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 403)
        new_employee_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

    def test_wrong_request_type(self):
        """
        Test whether other request types are supported
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 400)

    def test_errored_form_submission(self):
        """
        Test the form submission on incorrect variables
        """
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertEqual(len(new_customer_query), 0)
        self.assertEqual(response.status_code, 200)
