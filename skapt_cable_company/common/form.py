"""
Module for all Common Shared Forms
"""

from django.forms import ModelForm
from django.contrib.auth.models import User


class UserBaseForm(ModelForm):
    """
    Base Form for any User Data View or Edit
    """

    class Meta:
        """
        Meta Data for the Form
        """

        model = User
        exclude = []

    def __init__(self, *args, **kwargs):
        """
        Initialization
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"


class UserCreateForm(ModelForm):
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
