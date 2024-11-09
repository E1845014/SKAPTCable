"""
Module to contain all Payment App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("allPayments", views.get_all_payments, name="all_payments"),
    path("<str:username>/addPayment", views.add_customer_payment, name="add_payment"),
    path("<str:username>/payments", views.get_customer_payments, name="view_payments"),
]
