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
