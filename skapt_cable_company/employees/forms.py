"""
Module for all Employee App Related Forms
"""

from django.forms import ModelForm
from common.models import Employee


class EmployeeForm(ModelForm):
    """
    Class for Employee Form
    """

    class Meta:
        model = Employee
        exclude = ["user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"
