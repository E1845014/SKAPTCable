"""
Module to contain all Employees App View Controller Codes
"""

from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect

from common.models import Employee
from common.form import UserCreateForm

from .forms import EmployeeForm


@login_required
def index(request: HttpRequest):
    """
    Employees List Page View Controller
    """

    template = loader.get_template("employees.html")
    if request.method == "GET":
        if request.user.is_staff:  # type: ignore
            employees = Employee.objects.all()
            return HttpResponse(template.render({"employees": employees}, request))
        raise PermissionDenied
    raise BadRequest


@login_required
def add_employee(request: HttpRequest):
    """
    Add Employee
    """

    template = loader.get_template("add_employees.html")
    if request.method == "GET":
        user_form = UserCreateForm()
        employee_form = EmployeeForm()
        print(user_form.fields)
        return HttpResponse(
            template.render(
                {"user_form": user_form, "employee_form": employee_form}, request
            )
        )
    raise BadRequest
