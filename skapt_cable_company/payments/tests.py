"""
Module to contain all Payment App Tests
"""

from django.forms import Form

from common.tests import BaseTestCase
from common.models import Payment

# Create your tests here.


class PaymentBaseTestCase(BaseTestCase):
    """
    Base Test Functionalities for Payment App Testing
    """

    def setUp(self):
        """
        Setup Base Payment Test Cases
        """
        super().setUp()
        self.customer = self.generate_customers()[0]
        self.connections = self.generate_connection(customers=[self.customer])


class PaymentsTestCase(PaymentBaseTestCase):
    """
    Tests cases for testing Customer Payments
    """

    def setUp(self):
        """
        Setup Payments Test Cases
        """
        super().setUp()
        self.url = self.url = f"/customers/{self.customer.pk}/payments"

    def test_page_renders_for_employees(self):
        """
        Test if the payments page renders for employee user
        """
        self.login_as_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("payments.html")
        self.client.logout()
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the payments page not renders for non-employees
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_renders_for_correct_customer(self):
        """
        Test if the page renders for the customer
        """
        self.login_as_customer(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_show_all_payments(self):
        """
        Test if all the payments of the customer are shown
        """
        self.login_as_employee()
        response = self.client.get(self.url)
        payment_count = Payment.objects.filter(
            connection__customer=self.customer
        ).count()
        self.assertEqual(len(response.context["payments"]), payment_count)


class AddPaymentTestCase(PaymentBaseTestCase):
    """
    Tests cases for testing Add Customer Payment
    """

    def setUp(self):
        """
        Setup Payments Test Cases
        """
        super().setUp()
        self.url = self.url = f"/customers/{self.customer.pk}/addPayment"
        self.expected_form_fields = ["amount"]

    def test_page_renders_for_correct_employee(self):
        """
        Test if the page renders for Agent
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("add_payment.html")

    def test_page_not_renders_for_incorrect_employee(self):
        """
        Test if the page not renders for incorrect employees
        """

        self.login_as_employee(self.generate_employees(1)[0])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_renders_for_non_employee(self):
        """
        Test if the page not renders for non-employees
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_data_fields(self):
        """
        Test whether expected form fields are passed
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        self.assertIn("payment_form", response.context)
        payment_form: Form = response.context["payment_form"]
        for expected_form_field in self.expected_form_fields:
            self.assertIn(expected_form_field, payment_form.fields)

    def test_add_payment_as_employee(self):
        """
        Test Agent can add payment
        """
        self.login_as_employee(self.customer.agent)

        response = self.client.get(self.url)
        payment_form: Form = response.context["payment_form"]
        amount = 100
        request_object = payment_form.initial
        request_object["connection"] = self.connections[0].pk
        request_object["amount"] = amount
        response = self.client.post(self.url, request_object)
        payment_query = Payment.objects.filter(
            connection__customer=self.customer, amount=amount
        )
        self.assertTrue(payment_query.exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{self.customer.pk}/payments")

    def test_add_invalid_payment(self):
        """
        Test whether system can handle invalid payments
        """
        self.login_as_employee(self.customer.agent)
        amount = -100

        response = self.client.get(self.url)
        payment_form: Form = response.context["payment_form"]

        request_object = payment_form.initial
        request_object["amount"] = amount

        response = self.client.post(self.url, request_object)
        payment_query = Payment.objects.filter(
            connection__customer=self.customer, amount=amount
        )
        payment_form: Form = response.context["payment_form"]

        self.assertFalse(payment_query.exists())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("add_payment.html")
        self.assertFalse(payment_form.is_valid())

    def test_wrong_request_type(self):
        """
        Test whether other request types are not supported
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        payment_form: Form = response.context["payment_form"]
        request_object = payment_form.initial
        response = self.client.put(self.url, request_object)
        self.assertEqual(response.status_code, 400)


class ViewPaymentsTestCase(PaymentBaseTestCase):
    """
    Test Cases to test View Payments Page
    """

    url = "/customers/payments"

    def test_show_all_payments(self):
        """
        Test if all the payments of the customer are shown
        """
        self.login_as_employee()
        response = self.client.get(self.url)
        payment_count = Payment.objects.filter(
            connection__customer=self.customer
        ).count()
        self.assertEqual(len(response.context["payments"]), payment_count)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the payments page not renders for non-employees
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
