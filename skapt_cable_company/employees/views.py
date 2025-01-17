"""
Module to contain all Employees App View Controller Codes
"""

# pylint: disable=imported-auth-user

from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count

from common.models import Employee
from common.form import UserBaseForm

from .models import get_employee_or_super_admin, get_employee
from .forms import EmployeeForm


@login_required
def index(request: HttpRequest):
    """
    Employees List Page View Controller
    """
    template = loader.get_template("employees.html")
    if Employee.objects.filter(user=request.user).exists() or request.user.is_superuser:  # type: ignore
        employees = (
            Employee.objects.all()
            .select_related("user")
            .annotate(area_count=Count("area"))
        )
        return HttpResponse(template.render({"employees": employees}, request))
    raise PermissionDenied


@login_required
def add_employee(request: HttpRequest):
    """
    Add Employee
    """
    if not request.user.is_superuser:  # type: ignore
        request_employee = get_employee(request)
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
                if not request.user.is_superuser:  # type: ignore
                    if not request_employee.is_admin:
                        employee.is_admin = False
            employee.save()
            if request.user.is_superuser or request_employee.is_admin:  # type: ignore
                return redirect(f"/employees/{new_user.username}")
            return redirect("/employees")
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
def view_employee(request: HttpRequest, username: str):
    """
    Employee Page View Controller
    """
    template = loader.get_template("employee.html")
    employee = get_object_or_404(Employee, user__username=username)
    request_employee = get_employee_or_super_admin(request)
    if employee.is_accessible(request_employee):
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
    employee = get_object_or_404(Employee, user__username=username)
    request_employee = get_employee_or_super_admin(request)
    errors = []
    if employee.is_accessible(request_employee):
        if request.method == "GET":
            user_form = UserBaseForm(instance=employee.user)
            employee_form = EmployeeForm(instance=employee)
        elif request.method == "POST":
            user_form = UserBaseForm(request.POST, instance=employee.user)
            employee_form = EmployeeForm(request.POST, instance=employee)
            if user_form.is_valid() and employee_form.is_valid():
                new_user = user_form.save(commit=False)
                employee = employee_form.save(commit=False)
                new_user.username = employee.phone_number
                employee.is_admin = employee.is_admin and (request.user.is_superuser or request_employee.is_admin)  # type: ignore
                new_user.save()
                employee.save()
                return redirect(f"/employees/{new_user.username}")
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
