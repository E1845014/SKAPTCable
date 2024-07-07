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
from common.form import UserBaseForm

from .forms import EmployeeForm


@login_required
def index(request: HttpRequest):
    """
    Employees List Page View Controller
    """

    template = loader.get_template("employees.html")
    if request.method == "GET":
        if request.user.is_staff:  # type: ignore
            employees = Employee.objects.all().select_related("user")
            return HttpResponse(template.render({"employees": employees}, request))
        raise PermissionDenied
    raise BadRequest


@login_required
def add_employee(request: HttpRequest):
    """
    Add Employee
    """
    if not request.user.is_superuser:  # type: ignore
        try:
            request_employee = Employee.objects.get(user=request.user)
        except ObjectDoesNotExist:
            raise PermissionDenied
    template = loader.get_template("add_employees.html")
    errors = []
    if request.method == "GET":
        user_form = UserBaseForm()
        employee_form = EmployeeForm()
    elif request.method == "POST":
        user_form = UserBaseForm(request.POST)
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
                request_employee = None
                if not request.user.is_superuser:  # type: ignore
                    if not request_employee.is_admin:  # type: ignore
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


@login_required
def employee(request: HttpRequest, username: str):
    """
    Employee Page View Controller
    """
    template = loader.get_template("employee.html")
    employee = Employee.objects.get(user__username=username)
    if employee.is_accessible(request.user):
        user_form = UserBaseForm(instance=employee.user)
        employee_form = EmployeeForm(instance=employee)
        user_form.disable_fields()
        employee_form.disable_fields()
        return HttpResponse(
            template.render(
                {
                    "employee_form": employee_form,
                    "user_form": user_form,
                    "employee": employee,
                },
                request,
            )
        )
    raise PermissionDenied


@login_required
def update_employee(request: HttpRequest, username: str):
    """
    Update Employee Page View Controller
    """
    template = loader.get_template("update_employee.html")
    employee = Employee.objects.get(user__username=username)
    errors = []
    if employee.is_accessible(request.user):
        if request.method == "GET":
            user_form = UserBaseForm(instance=employee.user)
            employee_form = EmployeeForm(instance=employee)
        elif request.method == "POST":
            user_form = UserBaseForm(request.POST, instance=employee.user)
            employee_form = EmployeeForm(request.POST, instance=employee)
            if user_form.is_valid() and employee_form.is_valid():
                new_user = user_form.save(commit=False)
                employee = employee_form.save(commit=False)
                if (
                    not Employee.objects.filter(phone_number=employee.phone_number)
                    .exclude(user=employee.user)
                    .exists()
                ):
                    new_user.username = employee.phone_number
                    new_user.save()
                    employee.save()
                    return redirect(f"/employees/{new_user.username}")
                employee_form.add_error("phone_number", "Phone Number Already Exists")
        return HttpResponse(
            template.render(
                {
                    "employee_form": employee_form,
                    "user_form": user_form,
                    "employee": employee,
                    "notifications": [
                        {"message": error, "class_name": " is-danger"}
                        for error in errors
                    ],
                },
                request,
            )
        )
    raise PermissionDenied
