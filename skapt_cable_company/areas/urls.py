"""
Module to contain all Area App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add_area, name="add Area"),
    path("<int:area_id>", views.view_area, name="View Area"),
    path("<int:area_id>/update", views.update_area, name="Update Area"),
]
