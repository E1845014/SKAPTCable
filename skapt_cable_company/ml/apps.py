"""App Configuration for ML App"""

from django.apps import AppConfig


class MlConfig(AppConfig):
    """
    A Class to Do ML App Configurations
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "ML"
