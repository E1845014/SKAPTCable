"""
Module to contain all Payment App View Controller Codes
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import BadRequest, PermissionDenied
from django.core.paginator import Paginator

from common.models import Customer, Payment, Employee

from .forms import PaymentForm

# Create your views here.


@login_required
def get_all_payments(request: HttpRequest):
    """
    Get all Payments
    """
    if not Employee.objects.filter(user=request.user).exists():
        raise PermissionDenied
    template = loader.get_template("all_payments.html")
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
    payments = Payment.objects.all()
    paginator = Paginator(payments, size)
    return HttpResponse(
        template.render(
            {
                "paginator": paginator,
                "payments": paginator.page(page_number),
            },
            request,
        )
    )


@login_required
def add_customer_payment(request: HttpRequest, username: str):
    """
    Add Customer Payment
    """
    template = loader.get_template("add_payment.html")
    customer = get_object_or_404(Customer, pk=username)
    employee_query = Employee.objects.filter(user=request.user)
    if not employee_query.exists():
        raise PermissionDenied
    if customer.is_editable(request.user):
        if request.method == "GET":
            payment_form = PaymentForm(customer)
        elif request.method == "POST":
            payment_form = PaymentForm(None, request.POST)
            if payment_form.is_valid():
                payment = payment_form.save(False)
                payment.connection.customer = customer
                payment.employee = employee_query[0]
                payment.save()
                return redirect(f"/customers/{customer.pk}/payments")
        else:
            raise BadRequest
        return HttpResponse(
            template.render(
                {"payment_form": payment_form, "customer": customer}, request
            )
        )
    raise PermissionDenied


@login_required
def get_customer_payments(request: HttpRequest, username: str):
    """
    Get Customers Payments
    """
    template = loader.get_template("payments.html")
    customer = get_object_or_404(Customer, pk=username)
    if customer.is_accessible(request.user):
        payments = Payment.objects.filter(connection__customer=customer)
        return HttpResponse(
            template.render({"payments": payments, "customer": customer}, request)
        )
    raise PermissionDenied
