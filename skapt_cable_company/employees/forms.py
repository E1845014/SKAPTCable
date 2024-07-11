"""
Module for all Employee App Related Forms
"""

from typing import List, Union

from django.forms import ModelForm

from common.models import Employee
from common.form import disable_fields


class EmployeeForm(ModelForm):
    """
    Class for Employee Form
    """

    class Meta:
        """
        Meta Data for Employee Form
        """

        model = Employee
        fields = ["phone_number", "is_admin"]

    def __init__(self, *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.input_type == "text":
                field.widget.attrs["class"] = "input is-rounded"
                field.widget.attrs["placeholder"] = "Enter the Name of the Book"

    def disable_fields(self, fields: Union[None, List[str]] = None):
        """
        Disable given Fields
        """
        self.fields = disable_fields(self, fields)

    def save(self, commit=True) -> Employee:
        """
        Save Employee Form
        """
        return super().save(commit)
