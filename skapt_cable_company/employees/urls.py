"""
Module to contain all Employees App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add_employee, name="add Employee"),
    path("<str:username>", views.view_employee, name="View Employee"),
    path("<str:username>/update", views.update_employee, name="Update Employee"),
]
