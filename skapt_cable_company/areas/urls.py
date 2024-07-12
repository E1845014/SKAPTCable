"""
Module to contain all Area App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
