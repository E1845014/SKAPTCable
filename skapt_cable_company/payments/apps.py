"""App Configuration for Payment App"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Payment App Configuration Class
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
