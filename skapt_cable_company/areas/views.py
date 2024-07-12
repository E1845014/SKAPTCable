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
