"""
Module to contain all Customer View Controller Codes
"""

# pylint: disable=imported-auth-user

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User

from common.models import (
    Bill,
    Customer,
    Area,
    CustomerConnection,
    query_or_logic,
    pagination_handle,
)
from common.form import UserBaseForm

from employees.models import get_employee_or_super_admin, get_admin_employee

from .forms import CustomerForm
from .models import generate_customer_number


@login_required
def index(request: HttpRequest):
    """
    Customers List Page View Controller
    """
    if request.method == "GET":
        template = loader.get_template("customers.html")
        size, page_number = pagination_handle(request)
        search_text = request.GET.get("search_text")
        get_employee_or_super_admin(request)
        if search_text is None:
            customers = (
                Customer.objects.all()
                .order_by("connection_start_date")
                .select_related("user")
                .select_related("area")
                .select_related("area__agent")
                .select_related("area__agent__user")
            )
        else:
            # pylint: disable=unsupported-binary-operation
            customers = (
                Customer.objects.filter(
                    query_or_logic(
                        Q(customer_number__icontains=search_text),
                        Q(identity_no__icontains=search_text),
                        Q(user__first_name__icontains=search_text),
                        Q(user__last_name__icontains=search_text),
                    )
                )
                .order_by("connection_start_date")
                .select_related("user")
                .select_related("area")
                .select_related("area__agent")
                .select_related("area__agent__user")
            )
            # pylint: enable=unsupported-binary-operation
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


@login_required
def add_customer(request: HttpRequest):
    """
    Add Customer
    """
    if not request.user.is_superuser:  # type: ignore
        get_admin_employee(request)
    template = loader.get_template("add_customer.html")
    if request.method == "GET":
        customer_form = CustomerForm("ADD")
        user_form = UserBaseForm()
        if Area.objects.all().count() == 0:
            return redirect("/areas/add")
    elif request.method == "POST":
        user_form = UserBaseForm(request.POST)
        customer_form = CustomerForm("ADD", request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(False)
            customer = customer_form.save(False)
            customer.customer_number = generate_customer_number(customer)
            new_user = User.objects.create_user(
                customer.customer_number, user.email, customer.identity_no
            )
            new_user.first_name = user.first_name
            new_user.last_name = user.last_name
            new_user.save()
            customer.user = new_user
            customer.save()
            return redirect(f"/customers/{new_user.pk}")
    else:
        raise BadRequest
    return HttpResponse(
        template.render(
            {"user_form": user_form, "customer_form": customer_form},
            request,
        )
    )


@login_required
def view_customer(request: HttpRequest, username: str):
    """
    Customer Page View Controller
    """

    template = loader.get_template("customer.html")
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_accessible(request.user):
        customer_form = CustomerForm("VIEW", instance=customer)
        user_form = UserBaseForm(instance=customer.user)
        user_form.disable_fields()
        connections = CustomerConnection.objects.filter(customer=customer)
        return HttpResponse(
            template.render(
                {
                    "user_form": user_form,
                    "customer_form": customer_form,
                    "customer": customer,
                    "connections": connections,
                    "bills": customer.bills,
                },
                request,
            )
        )
    raise PermissionDenied


@login_required
def update_customer(request: HttpRequest, username: str):
    """
    Update Customer Page View Controller
    """
    template = loader.get_template("update_customer.html")
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_editable(request.user):
        if request.method == "GET":
            customer_form = CustomerForm("UPDATE", instance=customer)
            user_form = UserBaseForm(instance=customer.user)
        elif request.method == "POST":
            customer_form = CustomerForm("UPDATE", request.POST, instance=customer)
            user_form = UserBaseForm(request.POST, instance=customer.user)
            if user_form.is_valid() and customer_form.is_valid():
                new_user = user_form.save(False)
                new_customer = customer_form.save(False)
                if request.POST["area"] != customer.area.pk:
                    new_area = Area.objects.get(pk=request.POST["area"])
                    new_customer.area = new_area
                    new_customer.customer_number = generate_customer_number(
                        new_customer
                    )
                    new_user.username = new_customer.customer_number
                new_user.save()
                new_customer.save()
                return redirect(f"/customers/{new_user.pk}")
        else:
            raise BadRequest
        return HttpResponse(
            template.render(
                {
                    "customer_form": customer_form,
                    "user_form": user_form,
                    "customer": customer,
                },
                request,
            )
        )
    raise PermissionDenied


@login_required
def add_connection(request: HttpRequest, username: str):
    """
    Add Connection to the user
    """
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_editable(request.user) and request.GET["box_ca_number"] != "":
        customer_connection_exist = CustomerConnection.objects.filter(
            box_ca_number=request.GET["box_ca_number"]
        ).exists()
        if not customer_connection_exist:
            customer_connection = CustomerConnection(
                customer=customer,
                active=True,
                box_ca_number=request.GET["box_ca_number"],
            )
            customer_connection.save()
    return redirect(f"/customers/{customer.pk}")


@login_required
def enable_connection(request: HttpRequest, username: str, connection_id: int):
    """
    Enable Connection
    """
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_editable(request.user):
        connection = CustomerConnection.objects.get(pk=connection_id, customer=customer)
        connection.active = True
        connection.save()
        connection.generate_bill(
            end_date=datetime.now(),
            billing_amount=0,
            description=Bill.DescriptionChoices.ZeroReconnection,
        )
        return redirect(f"/customers/{customer.pk}")
    raise PermissionDenied


@login_required
def disable_connection(request: HttpRequest, username: str, connection_id: int):
    """
    Disable Connection
    """
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_editable(request.user):
        connection = CustomerConnection.objects.get(pk=connection_id, customer=customer)
        connection.active = False
        connection.save()
        connection.generate_bill(
            end_date=datetime.now(),
            description=Bill.DescriptionChoices.ZeroDisconnection,
        )
        return redirect(f"/customers/{customer.pk}")
    raise PermissionDenied
