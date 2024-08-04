"""
Module to contain all Customer View Controller Codes
"""

# pylint: disable=imported-auth-user

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User

from common.models import Customer, Area
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
        size = request.GET.get("size", "10")
        if size.isnumeric():
            size = int(size)
        else:
            size = 10
        page_number = request.GET.get("page", "1")
        if page_number.isnumeric():
            page_number = int(page_number)
        else:
            page_number = 1
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
            customers = (
                Customer.objects.filter(
                    Q(customer_number__icontains=search_text)
                    | Q(identity_no__icontains=search_text)
                    | Q(user__first_name__icontains=search_text)
                    | Q(user__last_name__icontains=search_text)
                )
                .order_by("connection_start_date")
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
        return HttpResponse(
            template.render(
                {
                    "user_form": user_form,
                    "customer_form": customer_form,
                    "customer": customer,
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
