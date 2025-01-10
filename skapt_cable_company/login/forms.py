"""
Module for all Login App Related Forms
"""

from typing import Any
from django import forms
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.forms import PasswordChangeForm


class LoginForm(forms.Form):
    """
    Class For Login Form
    """

    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"


class EmployeePasswordChangeForm(PasswordChangeForm):
    """
    Password Change form for Employees
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input is-rounded"
