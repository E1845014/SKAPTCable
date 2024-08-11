"""Module for Payment App Admin Pannel Integration"""

from django.contrib import admin

from common.models import Payment

admin.site.register(Payment)

# Register your models here.
