"""
Module to contain all Payment App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("<str:username>/addPayment", views.add_customer_payment, name="index")
]
