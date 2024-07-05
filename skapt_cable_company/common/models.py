"""
Module to contain all Common Models
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class Employee(models.Model):
    """
    Class For Employee Model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=10)
    is_admin = models.BooleanField(default=False)

    def is_accessible(self, user: User):
        """
        Method to check if the Employee can be accessible by the user
        """
        try:
            return self.user == user or self.objects.get(user=user).is_admin
        except ObjectDoesNotExist:
            return False

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
