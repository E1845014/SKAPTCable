"""
Module to contain all Employee Model Related Functions
"""

from django.http import HttpRequest
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from common.models import Employee


def get_employee_or_super_admin(request: HttpRequest):
    request_employee = request.user
    if not request_employee.is_superuser:  # type: ignore
        try:
            request_employee = Employee.objects.get(user=request.user)
        except ObjectDoesNotExist as exc:
            raise PermissionDenied from exc
    return request_employee
