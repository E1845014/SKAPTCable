"""
Module for all Common Models Tests
"""

# pylint: disable=imported-auth-user

from time import time
from typing import List, Union
from random import choices, choice, randint
from string import ascii_letters
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory

from ml.predictors import DelayPredictor, DefaultPredictor

from .models import (
    CustomerConnection,
    Employee,
    Area,
    Customer,
    Payment,
    Bill,
    pagination_handle,
)


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

    def get_random_n_digit_number(self, n: int):
        """
        Generate N legnth random Integer
        """
        range_start = 10 ** (n - 1)
        range_end = (10**n) - 1
        return randint(range_start, range_end)

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
                    identity_no=f"19{self.get_random_n_digit_number(10)}",
                    customer_number=self.get_random_string(),
                    area=choice(areas),
                )
            )
        return customers

    def generate_connection(self, n=5, customers: Union[List[Customer], None] = None):
        """
        Generate n number of connections
        """
        if customers is None:
            customers = self.generate_customers()
        connections: List[CustomerConnection] = []
        for _ in range(n):
            connections.append(
                CustomerConnection.objects.create(
                    customer=choice(customers), box_ca_number=self.get_random_string(10)
                )
            )
        return connections

    def generate_payments(
        self,
        n=5,
        customers: Union[List[Customer], None] = None,
        connections: Union[List[CustomerConnection], None] = None,
    ):
        """
        Generate n number of Payments
        """
        if connections is None:
            connections = self.generate_connection(n, customers)
        payments: List[Payment] = []
        for _ in range(n):
            connection = choice(connections)
            customer = connection.customer
            payments.append(
                Payment.objects.create(
                    connection=connection,
                    employee=customer.get_agent(),
                    amount=randint(1, 100),
                )
            )
        return payments

    def generate_bills(
        self, n=5, connections: Union[List[CustomerConnection], None] = None
    ):
        """
        Generate n number of Bills
        """
        connections = self.generate_connection(n)
        bills: List[Bill] = []
        for _ in range(n):
            bills.append(
                Bill.objects.create(
                    connection=choice(connections),
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

    def test_total_collected_payments_amount(self):
        """
        Test Total Collected Payments Amount
        """
        payments = self.generate_payments()
        employee = choice(payments).employee
        payments_collected_by_employee = Payment.objects.filter(employee=employee)
        total_amount = sum([payment.amount for payment in payments_collected_by_employee])
        self.assertEqual(employee.total_collected_payments_amount, total_amount)


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
        Test Area Accessibility by it's Agent
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
        Test Area is not editability by customer
        """
        customer = self.generate_customers(1)[0]
        self.assertFalse(customer.area.is_editable(customer))

    def test_customers(self):
        """
        Test Area's Customers are Populated
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
        Test Customer Model's String
        """
        customer = self.generate_customers(1)[0]
        self.assertEqual(str(customer), str(customer.user))

    def test_accessibility_by_themself(self):
        """
        Test Customer Accessibility by themself
        """
        customer = self.generate_customers(1)[0]
        self.assertTrue(customer.is_accessible(customer))

    def test_accessibility_by_agent(self):
        """
        Test Customer Accessibility by their Agent
        """
        customer = self.generate_customers(1)[0]
        self.assertTrue(customer.is_accessible(customer.get_agent()))

    def test_agent(self):
        """
        Test Customer's Agent is Populated
        """
        area = self.generate_areas(1)[0]
        customer = self.generate_customers(1, [area])[0]
        self.assertEqual(customer.agent, area.agent)

    def test_payments(self):
        """
        Test Customer's Payments Populated
        """
        customer = self.generate_customers(1)[0]
        payments = self.generate_payments(customers=[customer])
        for payment in customer.payments:
            self.assertIn(payment, payments)

    def test_age(self):
        """
        Test Customer's Age Calculation
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
        Test Customer's Gender
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
        Test if Expected Payment Date is returned
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

    def test_default_probability(self):
        """
        Test if Default Probability
        """
        default_predictor = DefaultPredictor()
        customer = self.generate_customers(1)[0]
        customer.identity_no = "199728402249"
        customer.phone_number = "0770068454"
        customer.save()
        area = Area.objects.get(pk=customer.area.pk)
        area.name = list(default_predictor.area_prob.keys())[0]
        area.save()
        agent = User.objects.get(pk=area.agent.user.pk)
        agent.first_name = list(default_predictor.agent_probs.keys())[0]
        agent.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.default_probability is not None)

        customer.phone_number = "0710068454"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.default_probability is not None)

        customer.phone_number = "0790068454"
        customer.save()
        customer = Customer.objects.get(pk=customer.pk)
        self.generate_payments(customers=[customer])
        self.assertTrue(customer.default_probability is not None)

    def test_bills(self):
        """
        Test Customer's Bills Populated
        """
        customer = self.generate_customers(1)[0]
        connections = self.generate_connection(customers=[customer])
        bills = self.generate_bills(connections=connections)
        for bill in customer.bills:
            self.assertIn(bill, bills)


class PaymentTestCase(BaseTestCase):
    """
    Test Cases to test Payment Model
    """

    def test_str(self):
        """
        Test Payment Model String
        """
        payment = self.generate_payments(1)[0]
        customer_name = payment.connection.customer.user.get_short_name()
        self.assertEqual(
            str(payment),
            f"{customer_name} paid {payment.amount} on {payment.date} to {payment.employee.user.get_short_name()}",
        )


class CustomerConnectionTestCase(BaseTestCase):
    """
    Test Cases to test Customer Connection Model
    """

    def test_str(self):
        """
        Test Customer Connection's String
        """
        connection = self.generate_connection(1)[0]
        self.assertEqual(
            str(connection),
            f"Connection {connection.id} by {connection.customer.user.get_short_name()}",
        )

    def test_monthly_bill_generation(self):
        """
        Test Bill Generation for monthly bill
        """
        connection = self.generate_connection(1)[0]
        connection.start_date = date.today() - timedelta(days=60)
        connection.generate_bill()
        self.assertTrue(connection.bills.exists())

    def test_bills(self):
        """
        Test Connection's Bills Populated
        """
        connection = self.generate_connection(1)[0]
        bills = self.generate_bills(connections=[connection])
        for bill in connection.bills:
            self.assertIn(bill, bills)

    def test_payments(self):
        """
        Test Connection's Payments Populated
        """
        connection = self.generate_connection(1)[0]
        payments = self.generate_payments(connections=[connection])
        for payment in connection.payments:
            self.assertIn(payment, payments)

    def test_balance(self):
        """
        Test Connection's Balance Calculation
        """
        connection = self.generate_connection(1)[0]
        payments = self.generate_payments(connections=[connection])
        total_payment = sum([payment.amount for payment in payments])
        total_bill = sum([bill.amount for bill in connection.bills])
        self.assertEqual(connection.balance, total_bill - total_payment)


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
            f"{bill.connection.customer.user.get_short_name()} billed {bill.amount} on {bill.date} for the duration from {bill.from_date} to {bill.to_date}",
        )


class PaginationHandleTestCase(BaseTestCase):
    """
    Test Cases to test Pagination Handler
    """

    def test_non_numerical(self):
        """
        Test Non Numerical Parameters
        """
        rf = RequestFactory()
        target_page = self.get_random_string()
        target_size = self.get_random_string()
        request = rf.get("", {"size": target_size, "page": target_page})
        size, page = pagination_handle(request)
        self.assertNotEqual(page, target_page)
        self.assertNotEqual(size, target_size)

    def test_numerical(self):
        """
        Test Numerical Parameters
        """
        rf = RequestFactory()
        target_page = 5
        target_size = 6
        request = rf.get("", {"size": target_size, "page": target_page})
        size, page = pagination_handle(request)
        self.assertEqual(page, target_page)
        self.assertEqual(size, target_size)
