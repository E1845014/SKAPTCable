"""
Module to contain all Area App View Controller Codes
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.core.exceptions import BadRequest, PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User

from common.models import Employee, Area
from common.form import UserBaseForm

from employees.forms import EmployeeForm

from .forms import AreaForm


@login_required
def index(request: HttpRequest):
    """
    Areas List Page View Controller
    """
    template = loader.get_template("areas.html")
    if Employee.objects.filter(user=request.user).exists() or request.user.is_superuser:  # type: ignore
        areas = Area.objects.all().select_related("agent").select_related("agent__user")
        return HttpResponse(template.render({"areas": areas}, request))
    raise PermissionDenied


@login_required
def add_area(request: HttpRequest):
    """
    Add Area
    """
    if not request.user.is_superuser:  # type: ignore
        try:
            request_employee = Employee.objects.get(user=request.user)
        except ObjectDoesNotExist as exc:
            raise PermissionDenied from exc
        if not request_employee.is_admin:
            raise PermissionDenied
    template = loader.get_template("add_areas.html")
    errors = []
    if request.method == "GET":
        area_form = AreaForm()
    elif request.method == "POST":
        area_form = AreaForm(request.POST)
        if area_form.is_valid:
            area = area_form.save(False)
            if Employee.objects.filter(pk=area.agent.pk).exists():
                area.save()
                return redirect(f"/areas/{area.pk}")
            area_form.add_error("agent", "Agent Does not Exist")
        errors.append("Invalid Input Data")
    else:
        raise BadRequest
    return HttpResponse(
        template.render(
            {
                "area_form": area_form,
                "notifications": [
                    {"message": error, "class_name": " is-danger"} for error in errors
                ],
            },
            request,
        )
    )


@login_required
def view_area(request: HttpRequest, area_id: int):
    """
    Area Page View Controller
    """
    template = loader.get_template("area.html")
    area = get_object_or_404(Area, pk=area_id)
    request_employee = request.user
    if not request_employee.is_superuser:  # type: ignore
        try:
            request_employee = Employee.objects.get(user=request.user)
        except ObjectDoesNotExist as exc:
            raise PermissionDenied from exc
    if area.agent.is_accessible(request_employee):
        area_form = AreaForm(instance=area)
        employee_form = EmployeeForm(instance=area.agent)
        user_form = UserBaseForm(instance=area.agent.user)
        area_form.disable_fields()
        return HttpResponse(
            template.render(
                {
                    "area_form": area_form,
                    "employee_form": employee_form,
                    "user_form": user_form,
                    "area": area,
                },
                request,
            )
        )
    raise PermissionDenied
