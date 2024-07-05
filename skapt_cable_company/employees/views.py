"""
Module to contain all Employees App View Controller Codes
"""

from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect

from common.models import Employee


@login_required
def index(request: HttpRequest):
    """
    Employees List Page View Controller
    """

    template = loader.get_template("employees.html")
    if request.method == "GET":
        if request.user.is_staff:  # type: ignore
            employees = Employee.objects.all()
            return HttpResponse(template.render({"employees": employees}))
        raise PermissionDenied
    raise BadRequest
