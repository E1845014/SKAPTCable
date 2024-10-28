"""
Module for all Common Models Tests
"""

# pylint: disable=imported-auth-user

from time import time
from typing import List, Union
from random import choices, choice, randint
from string import ascii_letters
from datetime import date, datetime

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Employee, Area, Customer, Payment, Bill
from ML.predictors import DelayPredictor


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
        initial_user_count = User.objects.count()
        for i in range(initial_user_count, initial_user_count + n):
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
        initial_user_count = User.objects.count()
        for i in range(initial_user_count, initial_user_count + n):
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
                    identity_no=f"19{self.get_random_string(10)}",
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

    def login_as_employee(
        self, employee: Union[Employee, None] = None, make_admin=False
    ):
        """
        Login Client as an employee
        """
        if employee is None:
            employee = self.generate_employees(1)[0]
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

    def login_as_customer(self, customer: Customer):
        """
        Login Client as customer
        """
        return self.client.login(
            username=customer.user.username, password=self.raw_password
        )

    def login_as_non_employee(self):
        """
        Login Client as a non employee
        """
        non_employee_user = User.objects.create_user(
            "username", "email@mail.co", self.raw_password
        )
        return self.client.login(
            username=non_employee_user.username, password=self.raw_password
        )

    def helper_non_render_test(
        self, url: str, non_employee: bool, non_admin_employee: bool
    ):
        """
        Checks page renders for user types
        """
        if non_admin_employee:
            self.login_as_employee()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)
        if non_employee:
            self.login_as_non_employee()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)


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

    def test_areas(self):
        """
        Test Areas populated
        """
        employee = self.generate_employees()[0]
        areas = self.generate_areas(employees=[employee])
        for area in employee.areas:
            self.assertIn(area, areas)

    def test_name(self):
        """
        Test Name of Employee
        """
        employee = self.generate_employees()[0]
        self.assertEqual(employee.name, employee.user.get_short_name())

    def test_collected_payments(self):
        """
        Test Payments Populated
        """
        payments = self.generate_payments()
        employee = choice(payments).employee
        for payment in Payment.objects.filter(employee=employee):
            self.assertIn(payment, employee.collected_payments)

    def test_customers(self):
        """
        Test Customer Populated
        """
        area = self.generate_areas(1)[0]
        customers = self.generate_customers(areas=[area])
        for customer in area.agent.customers:
            self.assertIn(customer, customers)

    def test_customer_payments(self):
        """
        Test Customer Payments Populated
        """
        area = self.generate_areas(1)[0]
        customers = self.generate_customers(areas=[area])
        payments = self.generate_payments(customers=customers)
        for payment in area.agent.customer_payments:
            self.assertIn(payment, payments)


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

    def test_editable_by_superuser(self):
        """
        Test Area Editability by superuser
        """
        superuser = User.objects.create_superuser("username", None, "password")
        area = self.generate_areas(1)[0]
        self.assertTrue(area.is_editable(superuser))

    def test_editable_by_agent(self):
        """
        Test Area Editability by the agent
        """
        area = self.generate_areas(1)[0]
        self.assertTrue(area.is_editable(area.agent))

    def test_editable_by_customer(self):
        """
        Test Area editability by customer
        """
        customer = self.generate_customers(1)[0]
        self.assertFalse(customer.area.is_editable(customer))

    def test_customers(self):
        """
        Test Area Customers Populated
        """
        area = self.generate_areas(1)[0]
        customers = self.generate_customers(areas=[area])
        for customer in area.customers:
            self.assertIn(customer, customers)

    def test_customer_payments(self):
        """
        Test Area Customer Payments Populated
        """
        area = self.generate_areas(1)[0]
        customers = self.generate_customers(areas=[area])
        payments = self.generate_payments(customers=customers)
        for payment in area.customer_payments:
            self.assertIn(payment, payments)


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

    def test_agent(self):
        """
        Test Customer Agent Populated
        """
        area = self.generate_areas(1)[0]
        customer = self.generate_customers(1, [area])[0]
        self.assertEqual(customer.agent, area.agent)

    def test_payments(self):
        """
        Test Customer Payments Populated
        """
        customer = self.generate_customers(1)[0]
        payments = self.generate_payments(customers=[customer])
        for payment in customer.payments:
            self.assertIn(payment, payments)

    def test_age(self):
        """
        Test Customer Age Calculation
        """
        customer = self.generate_customers(1)[0]
        customer.identity_no = "199728402249"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.assertEqual(customer.age, datetime.now().year - 1997)
        customer.identity_no = "972842249v"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.assertEqual(customer.age, datetime.now().year - 1997)

    def test_gender(self):
        """
        Test Customer Gender Calculation
        """
        customer = self.generate_customers(1)[0]
        customer.identity_no = "199768402249"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.assertFalse(customer.is_male)
        customer.identity_no = "972842249v"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.assertTrue(customer.is_male)

    def test_payment_date(self):
        """
        Test if Payment Date is returned
        """
        delay_predictor = DelayPredictor()
        customer = self.generate_customers(1)[0]
        customer.identity_no = "199728402249"
        customer.phone_number = "0770068454"
        customer.save()
        area = Area.objects.get(pk=customer.area.pk)
        area.name = delay_predictor.areas[0]
        area.save()
        agent = User.objects.get(pk=area.agent.user.pk)
        agent.first_name = delay_predictor.agent[0]
        agent.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.expected_payment_date is not None)
        
        customer.phone_number = "0710068454"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.expected_payment_date is not None)

        customer.phone_number = "0790068454"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.expected_payment_date is not None)


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
