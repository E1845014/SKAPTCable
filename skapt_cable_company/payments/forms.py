"""
Module for all Payment App Related Forms
"""

from django.forms import ModelForm

from common.models import Payment
from common.form import (
    SKAPTTextInput,
)


class PaymentForm(ModelForm):
    """
    Class for Payment Form
    """

    class Meta:
        """
        Meta Data for Payment Form
        """

        model = Payment
        widgets = {
            "amount": SKAPTTextInput(attrs={"type": "number"}),
        }
        fields = widgets.keys()

    def __init__(self, *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)

    def save(self, commit=True) -> Payment:
        """
        Save Employee Form
        """
        return super().save(commit)
