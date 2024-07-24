from django.forms import Form
from datetime import date

from common.tests import BaseTestCase

# Create your tests here.


class AddCustomerTestCase(BaseTestCase):

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
        customer_form : Form = get_response.context["customer_form"]
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
