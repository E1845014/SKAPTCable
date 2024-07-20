"""
Module for all Areas App Related Forms
"""

from typing import List, Union

from django.forms import ModelForm

from common.models import Area
from common.form import disable_fields


class AreaForm(ModelForm):
    """
    Class for Area Form
    """

    class Meta:
        """
        Meta Data for Area Form
        """

        model = Area
        fields = ["name", "agent"]

    def __init__(self, *args, **kwargs):
        """
        Form Initialization
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.input_type == "text":
                field.widget.attrs["class"] = "input is-rounded"
            elif field.widget.input_type == "select":
                field.widget.attrs["class"] = "input is-rounded is-info"
                field.widget.required = True

    def disable_fields(self, fields: Union[None, List[str]] = None):
        """
        Disable given Fields
        """
        self.fields = disable_fields(self, fields)

    def save(self, commit=True) -> Area:
        """
        Save Area Form
        """
        return super().save(commit)
