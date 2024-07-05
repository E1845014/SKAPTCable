"""
Module to contain all Employees App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/add", views.add_employee, name="add Employee"),
]
