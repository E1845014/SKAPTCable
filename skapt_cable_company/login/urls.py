"""
Module to contain all Login App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("accounts/login/", views.index, name="index"),
    path("home", views.home, name="home"),
    path("logout", views.logout_user, name="logout"),
    path("password", views.update_password, name="update_password"),
]
