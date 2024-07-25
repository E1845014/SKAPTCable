"""
Module for all Customers App Related Forms
"""

from typing import List, Union, Literal

from django.forms import ModelForm

from common.models import Customer
from common.form import (
    disable_fields,
    SKAPTTextArea,
    SKAPTTextInput,
    SKAPTDateInput,
    SKAPTChoiceInput,
)


class CustomerForm(ModelForm):
    """
    Customer Form for Add or Update Customer
    """

    class Meta:
        """
        Meta Data for Customer Form
        """

        model = Customer
        fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "customer_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "under_repair",
            "connection_start_date",
            "area",
        ]
        widgets = {
            "phone_number": SKAPTTextInput(attrs={"type": "number"}),
            "address": SKAPTTextArea(),
            "identity_no": SKAPTTextInput(),
            "box_ca_number": SKAPTTextInput(),
            "customer_number": SKAPTTextInput(),
            "connection_start_date": SKAPTDateInput(),
            "area": SKAPTChoiceInput(),
        }

    def __init__(self, action: Literal["ADD", "UPDATE", "VIEW"], *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)
        if action == "ADD":
            del self.fields["customer_number"]
            del self.fields["under_repair"]
        elif action == "VIEW":
            self.disable_fields()
        else:
            del self.fields["customer_number"]


    def disable_fields(self, fields: Union[None, List[str]] = None):
        """
        Disable given Fields
        """
        self.fields = disable_fields(self, fields)

    def save(self, commit=True) -> Customer:
        """
        Save Employee Form
        """
        return super().save(commit)
