"""
Module to contain all Employees App View Controller Codes
"""

from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib.auth.models import User

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
    try:
        request_employee = Employee.objects.get(user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied
    template = loader.get_template("add_employees.html")
    errors = []
    if request.method == "GET":
        user_form = UserCreateForm()
        employee_form = EmployeeForm()
    elif request.method == "POST":
        user_form = UserCreateForm(request.POST)
        employee_form = EmployeeForm(request.POST)
        if user_form.is_valid() and employee_form.is_valid():
            user: User = user_form.save(commit=False)
            employee: Employee = employee_form.save(False)
            new_user = User.objects.create_user(
                employee.phone_number, user.email, employee.phone_number
            )
            new_user.first_name = user.first_name
            new_user.last_name = user.last_name
            new_user.save()
            employee.user = new_user
            if employee.is_admin:
                if not request_employee.is_admin:
                    employee.is_admin = False
            employee.save()
            return redirect(f"/employees/{new_user.username}")
        errors.append("Invalid Input Data")
    else:
        raise BadRequest
    return HttpResponse(
        template.render(
            {
                "user_form": user_form,
                "employee_form": employee_form,
                "notifications": [
                    {"message": error, "class_name": " is-danger"} for error in errors
                ],
            },
            request,
        )
    )
