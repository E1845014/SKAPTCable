"""
Module to contain all Customers App View Controller Codes
"""

# pylint: disable=imported-auth-user

from django.contrib.auth.models import User
from django.forms import Form
from datetime import date

from common.tests import BaseTestCase


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

    def test_shows_all_employees(self):
        """
        Test if all the employees are shown
        """
        customers = self.generate_customers()
        self.login_as_employee(customers[0].area.agent)
        response = self.client.get("/customers/")
        self.assertEqual(len(response.context["customers"]), len(customers))


class AddCustomerTestCase(CustomerBaseTestCase):

    def setUp(self):
        """
        Setup Add Area Testings
        """

        self.url = "/customers/add"
        self.expected_form_fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "customer_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "under_repair",
            "connection_start_date",
            "area",
        ]
        return super().setUp()

    def test_post_request(self):
        area = self.generate_areas(1)[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_employee_phone_number = self.get_random_phone_number()
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
                request_object[field] = new_employee_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
