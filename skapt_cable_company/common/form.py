"""
Module for all Common Shared Forms
"""

from django.forms import ModelForm
from django.contrib.auth.models import User

from typing import List


class UserBaseForm(ModelForm):
    """
    Form for creating new User
    """

    class Meta:
        """
        Meta Data for the Form
        """

        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        """
        Initialization
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"

    def disable_fields(self, fields: List[str] = []):
        for field_name, field in self.fields.items():
            if fields == [] or field_name in fields:
                field.widget.attrs["readonly"] = True
                field.widget.attrs["style"] = "cursor: default;"
                field.disabled = True

    def save(self, commit=True, *args, **kwargs) -> User:
        return super().save(commit)
