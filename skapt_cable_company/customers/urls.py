"""
Module to contain all Customer App URLs
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add_customer, name="add Customer"),
    path("<str:username>", views.view_customer, name="View Customer"),
    path("<str:username>/update", views.update_customer, name="Update Customer"),
    path(
        "<str:username>/addConnection",
        views.add_connection,
        name="Add Customer Connection",
    ),
    path(
        "<str:username>/<str:connection_id>/enableConnection",
        views.enable_connection,
        name="Enable Customer Connection",
    ),
    path(
        "<str:username>/<str:connection_id>/disableConnection",
        views.disable_connection,
        name="Disable Customer Connection",
    ),
]
