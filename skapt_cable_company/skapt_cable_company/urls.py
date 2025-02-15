"""This handles all the urls of the project"""

from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("employees/", include("employees.urls")),
    path("areas/", include("areas.urls")),
    path("", include("payments.urls")),
    path("customers/", include("customers.urls")),
    path("", include("login.urls")),
]
