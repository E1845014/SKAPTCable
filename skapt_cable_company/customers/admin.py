"""
Module for Customer App Admin Pannel Integration
"""

from django.contrib import admin

from common.models import Customer

admin.site.register(Customer)
