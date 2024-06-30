"""App Configuration for Login App"""

from django.apps import AppConfig


class LoginConfig(AppConfig):
    """
    A Class to Do Login App Configurations
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "login"
