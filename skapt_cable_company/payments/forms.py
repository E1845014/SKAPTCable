"""
Module for all Payment App Related Forms
"""

from typing import Union
from django.forms import ModelForm

from common.models import CustomerConnection, Payment, Customer
from common.form import (
    SKAPTChoiceInput,
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
            "connection": SKAPTChoiceInput(),
        }
        fields = widgets.keys()

    def __init__(self, customer: Union[Customer, None], *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)
        if customer is not None:
            self.fields["connection"].queryset = CustomerConnection.objects.filter(  # type: ignore
                customer__pk=customer.pk
            )

    def save(self, commit=True) -> Payment:
        """
        Save Employee Form
        """
        return super().save(commit)
