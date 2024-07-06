"""
Module to contain all Common Models
"""

from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator

from typing import Union


class Employee(models.Model):
    """
    Class For Employee Model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"07\d\d\d\d\d\d\d\d",
                message="Enter Valid Phone Number",
                code="Invalid Phone Number",
            )
        ],
    )
    is_admin = models.BooleanField(default=False)

    def is_accessible(self, user: Union[User, AbstractBaseUser, AnonymousUser]):
        """
        Method to check if the Employee can be accessible by the user
        """
        if isinstance(user, AnonymousUser):
            return False
        if isinstance(user, User):
            return self.user == user or user.is_staff or user.is_superuser

    def get_areas(self):
        """
        Get Areas under control
        """
        return []

    def get_my_customers(self):
        """
        Get Customers under Areas
        """
        return []

    def get_collected_payments(self):
        """
        Get Payments Collected by the Employee
        """
        return []
