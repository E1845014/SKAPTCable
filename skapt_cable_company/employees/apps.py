"""App Configuration for Employees App"""

from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    """
    A Class to Do Employees App Configurations
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"
