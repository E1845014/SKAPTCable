"""
Module to contain all Common Models
"""

# pylint: disable=imported-auth-user

from typing import Union
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, AnonymousUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from numpy import zeros, array

from ml.predictors import DelayPredictor


def query_or_logic(*args):
    """
    Function to use to apply or condition among Q Objects in Django without Pylint throwing errors
    """
    first_query = args[0]
    if len(args) > 1:
        for arg in args[1:]:
            first_query = first_query | arg
    return first_query


class Employee(models.Model):
    """
    Class For Employee Model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"07\d\d\d\d\d\d\d\d",
                message="Enter Valid Phone Number",
                code="Invalid Phone Number",
            )
        ],
    )
    is_admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    def is_accessible(self, user: Union[User, AbstractBaseUser, AnonymousUser, object]):
        """
        Method to check if the Employee can be accessible by the user
        """
        if isinstance(user, User):
            return self.user == user or user.is_superuser
        if isinstance(user, Customer):
            return user.get_agent() == self
        return user.is_admin or (self.is_accessible(user.user))  # type: ignore

    @property
    def areas(self):
        """
        Get All Areas
        """
        return Area.objects.filter(agent=self)

    @property
    def name(self):
        """
        Get Employee Name
        """
        return self.user.get_short_name()

    @property
    def collected_payments(self):
        """
        Get Payments collected by this employee
        """
        return Payment.objects.filter(employee=self)

    @property
    def customers(self):
        """
        Get Customers managed by this employee
        """
        return Customer.objects.filter(area__agent=self)

    @property
    def customer_payments(self):
        """
        Get Payments of the employee managed area customers
        """
        return Payment.objects.filter(customer__area__agent=self)


class Area(models.Model):
    """
    Class for Area Model
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    agent = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    collection_date = models.SmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(0, "Has to be higher than zero"),
            MaxValueValidator(30, "Has to be less than 30"),
        ],
    )

    def __str__(self) -> str:
        return self.name

    def is_accessible(self, user: Union[User, AbstractBaseUser, AnonymousUser, object]):
        """
        Method to check if the Area can be accessible by the user
        """
        return self.agent.is_accessible(user)

    def is_editable(self, user: Union[User, AbstractBaseUser, AnonymousUser, object]):
        """
        Method to check if the Area can be editable by the user
        """
        if isinstance(user, User):
            return user.is_superuser
        if isinstance(user, Employee):
            return user.is_admin or user == self.agent
        return False

    @property
    def customers(self):
        """
        Get customers in this area
        """
        return Customer.objects.filter(area=self)

    @property
    def customer_payments(self):
        """
        Get Customer Payments in this area
        """
        return Payment.objects.filter(customer__area=self)


class Customer(models.Model):
    """
    Class For Customer Model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    phone_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"07\d\d\d\d\d\d\d\d",
                message="Enter Valid Phone Number",
                code="Invalid Phone Number",
            )
        ],
    )
    address = models.TextField()
    identity_no = models.CharField(max_length=12)
    box_ca_number = models.CharField(max_length=16, unique=True)
    customer_number = models.CharField(max_length=5, unique=True)
    active_connection = models.BooleanField(default=True)
    has_digital_box = models.BooleanField(default=True)
    offer_power_intake = models.BooleanField(default=False)
    under_repair = models.BooleanField(default=False)
    connection_start_date = models.DateField(default=now())
    area = models.ForeignKey(Area, on_delete=models.RESTRICT)

    def __str__(self):
        return str(self.user)

    def get_agent(self):
        """
        Get Agent of the Customer
        """
        return self.area.agent

    def is_accessible(
        self, user: Union[User, AbstractBaseUser, AnonymousUser, Employee, object]
    ):
        """
        Method to check if the Employee can be accessible by the user
        """
        if isinstance(user, User):
            employee_query = Employee.objects.filter(user=user).first()
            return (
                self.user == user
                or user.is_superuser
                or (employee_query is not None and self.is_accessible(employee_query))
            )
        if isinstance(user, Employee):
            return True
        return self.is_accessible(user.user)  # type: ignore

    def is_editable(self, user: Union[User, AbstractBaseUser, AnonymousUser, object]):
        """
        Method to check if the Employee can be Editable by the user
        """
        if isinstance(user, Employee):
            return user.is_admin or self.get_agent() == user
        employee_query = Employee.objects.filter(user=user).first()
        return user.is_superuser or (employee_query is not None and self.is_editable(employee_query))  # type: ignore

    @property
    def age(self):
        """
        Method to get the Age of the customer
        """
        if len(self.identity_no) == 12:
            return datetime.now().year - int(self.identity_no[:4])
        return datetime.now().year - (1900 + int(self.identity_no[:2]))

    @property
    def is_male(self):
        """
        Method to get the Gender of the customer
        """
        if len(self.identity_no) == 10:
            gender_code = int(self.identity_no[2:5])
        else:
            gender_code = int(self.identity_no[4:7])
        return gender_code < 500

    @property
    def expected_payment_date(self):
        """
        Get Payment Delay
        """
        pay_date = self.area.collection_date
        delay_predictor = DelayPredictor()
        payments = Payment.objects.filter(customer=self).order_by("date")[
            : delay_predictor.time_series_offset
        ]
        payments_array = (
            zeros(delay_predictor.time_series_offset)
            + delay_predictor.time_series_offset
        )
        for i, payment in enumerate(payments):
            payments_array[(delay_predictor.time_series_offset - len(payments)) + i] = (
                payment.date.day - pay_date
            )
        std_numerical_array = delay_predictor.normalize(
            payments_array, self.age, pay_date
        )
        area_array = delay_predictor.get_area_array(self.area.name)
        agent_array = delay_predictor.get_agent_array(self.area.agent.user.first_name)
        cell_array = delay_predictor.get_cell_career_array(self.phone_number)

        model = delay_predictor.get_model()
        date = datetime.today()
        return datetime(date.year, date.month, pay_date) + timedelta(
            days=(
                model.predict(
                    array(
                        list(std_numerical_array)
                        + list(area_array)
                        + [int(self.is_male)]
                        + [int(self.has_digital_box)]
                        + list(cell_array)
                        + list(agent_array)
                    ).reshape((1, -1))
                )[0]
                // 7
            )
            * 7
            + pay_date
        )

    @property
    def agent(self):
        """
        Get Agent
        """
        return self.area.agent

    @property
    def payments(self):
        """
        Get Payments
        """
        return Payment.objects.filter(customer=self)


class Payment(models.Model):
    """
    Class for Payment Model
    """

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    date = models.DateField(auto_now_add=True)
    amount = models.FloatField(
        validators=[MinValueValidator(0, message="Value has to be a positive number")]
    )

    def __str__(self):
        return f"{self.customer.user.get_short_name()} paid {self.amount} on {self.date} to {self.employee.user.get_short_name()}"


class Bill(models.Model):
    """
    Class for Bill Model
    """

    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    date = models.DateField(auto_now_add=True)
    from_date = models.DateField()
    to_date = models.DateField()
    amount = models.FloatField(
        validators=[MinValueValidator(0, message="Value has to be a positive number")]
    )

    def __str__(self):
        return f"{self.customer.user.get_short_name()} billed {self.amount} on {self.date} for the duration from {self.from_date} to {self.to_date}"
