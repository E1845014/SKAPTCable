"""
Module for all Common Shared Forms
"""

from django.forms import ModelForm
from django.contrib.auth.models import User


class UserBaseForm(ModelForm):

    class Meta:
        model = User
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"


class UserCreateForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"
