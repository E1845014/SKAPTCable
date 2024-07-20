"""
Module for all Common Models Tests
"""

# pylint: disable=imported-auth-user

from time import time
from typing import List, Union
from random import choices, choice, randint
from string import ascii_letters
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Employee, Area, Customer, Payment, Bill


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
                username=f"employee_{int(time())}{i}",
                email=f"employee_{int(time())}@{i}xz.com",
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

    def generate_customers(self, n=5, areas: Union[None, List[Area]] = None):
        """
        Generate n Number of Customers
        """
        if areas is None:
            areas = self.generate_areas()
        customers: List[Customer] = []
        for i in range(n):
            user = User.objects.create_user(
                username=f"customer_{int(time())}{i}",
                email=f"customer_{int(time())}@{i}xz.com",
                password=self.raw_password,
            )
            customers.append(
                Customer.objects.create(
                    user=user,
                    phone_number=self.get_random_phone_number(),
                    address=self.get_random_string(20),
                    identity_no=self.get_random_string(12),
                    box_ca_number=self.get_random_string(16),
                    customer_number=self.get_random_string(),
                    area=choice(areas),
                )
            )
        return customers

    def generate_payments(self, n=5, customers: Union[List[Customer], None] = None):
        """
        Generate n number of Payments
        """
        if customers is None:
            customers = self.generate_customers()
        payments: List[Payment] = []
        for _ in range(n):
            payments.append(
                Payment.objects.create(
                    customer=choice(customers),
                    employee=choice(customers).get_agent(),
                    amount=randint(1, 100),
                )
            )
        return payments

    def generate_bills(self, n=5, customers: Union[List[Customer], None] = None):
        """
        Generate n number of Bills
        """
        if customers is None:
            customers = self.generate_customers()
        bills: List[Bill] = []
        for _ in range(n):
            bills.append(
                Bill.objects.create(
                    customer=choice(customers),
                    from_date=date.today(),
                    to_date=date.today(),
                    amount=randint(1, 100),
                )
            )
        return bills

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


class EmployeeTestCase(BaseTestCase):
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

    def test_accessible_by_customer(self):
        """
        Test Employee's accessiblity by a customer
        """
        customer = self.generate_customers(1)[0]
        self.assertTrue(customer.get_agent().is_accessible(customer))


class AreaTestCase(BaseTestCase):
    """
    Test Cases to test Area Model
    """

    def test_str(self):
        """
        Test Area Models String
        """
        area = self.generate_areas(1)[0]
        self.assertEqual(str(area), area.name)

    def test_accessibility_by_agent(self):
        """
        Test Area Accessibility
        """
        area = self.generate_areas(1)[0]
        self.assertTrue(area.is_accessible(area.agent))


class CustomerTestCase(BaseTestCase):
    """
    Test cases to test Customer Model
    """

    def test_str(self):
        """
        Test Customer Model String
        """
        customer = self.generate_customers(1)[0]
        self.assertEqual(str(customer), str(customer.user))

    def test_accessibility_by_themself(self):
        """
        Test Customer Accessibility
        """
        customer = self.generate_customers(1)[0]
        self.assertTrue(customer.is_accessible(customer))

    def test_accessibility_by_agent(self):
        """
        Test Customer Accessibility by Admin
        """
        customer = self.generate_customers(1)[0]
        self.assertTrue(customer.is_accessible(customer.get_agent()))


class PaymentTestCase(BaseTestCase):
    """
    Test Cases to test Payment Model
    """

    def test_str(self):
        """
        Test Payment Model String
        """
        payment = self.generate_payments(1)[0]
        self.assertEqual(
            str(payment),
            f"{payment.customer.user.get_short_name()} paid {payment.amount} on {payment.date} to {payment.employee.user.get_short_name()}",
        )


class BillTestCase(BaseTestCase):
    """
    Test Cases to test Bill Model
    """

    def test_str(self):
        """
        Test Bill Model String
        """
        bill = self.generate_bills(1)[0]
        self.assertEqual(
            str(bill),
            f"{bill.customer.user.get_short_name()} billed {bill.amount} on {bill.date} for the duration from {bill.from_date} to {bill.to_date}",
        )
