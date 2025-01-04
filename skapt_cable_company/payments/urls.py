"""
Module to contain all Payment App URLs
"""

from django.urls import path

from . import views

customerUrlpatterns = [
    path(
        "customers/<str:username>/addPayment",
        views.add_customer_payment,
        name="add_payment",
    ),
    path(
        "customers/<str:username>/payments",
        views.get_customer_payments,
        name="view_payments",
    ),
]

paymentsUrlPatterns = [
    path("payments", views.get_all_payments, name="all_payments"),
]

urlpatterns = customerUrlpatterns + paymentsUrlPatterns
