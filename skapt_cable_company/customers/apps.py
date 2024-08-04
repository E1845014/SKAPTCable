"""App Configuration for Customer App"""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """
    A Class to Do Customer App Configurations
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "customers"
