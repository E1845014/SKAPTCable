"""
Module to contain all Area App View Controller Codes
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect, get_object_or_404

from common.models import Employee, Area
from common.form import UserBaseForm

from employees.forms import EmployeeForm
from employees.models import get_employee_or_super_admin, get_admin_employee

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
        get_admin_employee(request)
    template = loader.get_template("add_areas.html")
    errors = []
    if request.method == "GET":
        area_form = AreaForm()
    elif request.method == "POST":
        area_form = AreaForm(request.POST)
        if area_form.is_valid():
            area = area_form.save()
            return redirect(f"/areas/{area.pk}")
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
    request_employee = get_employee_or_super_admin(request)
    if area.agent.is_accessible(request_employee):
        area_form = AreaForm(instance=area)
        employee_form = EmployeeForm(instance=area.agent)
        user_form = UserBaseForm(instance=area.agent.user)
        employee_form.disable_fields()
        user_form.disable_fields()
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


@login_required
def update_area(request: HttpRequest, area_id: int):
    """
    Update Area Page View Controller
    """
    template = loader.get_template("update_area.html")
    area = get_object_or_404(Area, pk=area_id)
    request_employee = get_employee_or_super_admin(request)
    if area.agent.is_accessible(request_employee):
        if request.method == "GET":
            area_form = AreaForm(instance=area)
        elif request.method == "POST":
            area_form = AreaForm(request.POST, instance=area)
            if area_form.is_valid():
                area = area_form.save()
                return redirect(f"/areas/{area.pk}")
        else:
            raise BadRequest
        return HttpResponse(
            template.render(
                {"area_form": area_form, "area": area},
                request,
            )
        )
    raise PermissionDenied
