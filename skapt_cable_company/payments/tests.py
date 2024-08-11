"""
Module to contain all Payment App Tests
"""

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
        payment_count = Payment.objects.filter(customer=self.customer).count()
        self.assertEqual(len(response.context["payments"]), payment_count)
