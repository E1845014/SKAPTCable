"""
Module to contain all Area Customer View Controller Codes
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from common.models import Customer

from employees.models import get_employee_or_super_admin, get_admin_employee


@login_required
def index(request: HttpRequest):
    """
    Customers List Page View Controller
    """
    if request.method == "GET":
        template = loader.get_template("customers.html")
        size = request.GET.get("size", "10")
        if size.isnumeric():
            size = int(size)
        else:
            size = 10
        page_number = request.GET.get("page_number", "1")
        if page_number.isnumeric():
            page_number = int(page_number)
        else:
            page_number = 1
        search_text = request.GET.get("search_text")
        get_employee_or_super_admin(request)
        if search_text is None:
            customers = (
                Customer.objects.all()
                .select_related("user")
                .select_related("area")
                .select_related("area__agent")
                .select_related("area__agent__user")
            )
        else:
            customers = (
                Customer.objects.filter(
                    Q(customer_name__icontains=search_text)
                    | Q(identity_no__icontains=search_text)
                    | Q(user__first_name__icontains=search_text)
                    | Q(user__last_name__icontains=search_text)
                )
                .select_related("user")
                .select_related("area")
                .select_related("area__agent")
                .select_related("area__agent__user")
            )
        p = Paginator(customers, size)
        return HttpResponse(
            template.render(
                {
                    "paginator": p,
                    "customers": p.page(page_number),
                },
                request,
            )
        )
    raise BadRequest
