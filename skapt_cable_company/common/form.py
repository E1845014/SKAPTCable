"""
Module for all Common Shared Forms
"""

# pylint: disable=imported-auth-user

from typing import Any, List, Union

from django.forms import (
    ModelForm,
    Textarea,
    TextInput,
    DateInput,
    Select,
)
from django.contrib.auth.models import User


def disable_fields(form: ModelForm, fields: Union[None, List[str]] = None):
    """
    Disable Form Fields
    """
    if fields is None:
        fields = []
    for field_name, field in form.fields.items():
        if fields == [] or field_name in fields:
            field.widget.attrs["readonly"] = True
            field.widget.attrs["style"] = "cursor: default;"
    return form.fields


class SKAPTTextArea(Textarea):

    def __init__(self, attrs: Union[dict[str, Any], None] = None, **kwargs) -> None:
        super().__init__(attrs, **kwargs)
        self.attrs["class"] = "textarea is-rounded"


class SKAPTTextInput(TextInput):

    def __init__(self, attrs: Union[dict[str, Any], None] = None, **kwargs) -> None:
        super().__init__(attrs, **kwargs)
        self.attrs["class"] = "input is-rounded"


class SKAPTDateInput(DateInput):

    def __init__(
        self,
        attrs: Union[dict[str, Any], None] = None,
        format: Union[str, None] = None,
        **kwargs
    ) -> None:
        super().__init__(attrs, format, **kwargs)
        self.attrs["class"] = "input is-rounded"


class SKAPTChoiceInput(Select):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "input is-rounded"


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

    def disable_fields(self, fields: Union[None, List[str]] = None):
        """
        Disable All Fields
        """
        self.fields = disable_fields(self, fields=fields)

    def save(self, commit=True) -> User:
        """
        Save User Form
        """
        return super().save(commit)
