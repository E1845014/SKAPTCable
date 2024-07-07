"""
Module for all Employee App Related Forms
"""

from typing import List
from django.forms import ModelForm
from common.models import Employee


class EmployeeForm(ModelForm):
    """
    Class for Employee Form
    """

    class Meta:
        """
        Meta Data for Employee Form
        """

        model = Employee
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.input_type == "text":
                field.widget.attrs["class"] = "input is-rounded"
                field.widget.attrs["placeholder"] = "Enter the Name of the Book"

    def disable_fields(self, fields: List[str] = []):
        for field_name, field in self.fields.items():
            if fields == [] or field_name in fields:
                field.widget.attrs["readonly"] = True
                field.widget.attrs["style"] = "cursor: default;"
                field.disabled = True

    def save(self, commit=True) -> Employee:
        return super().save(commit)