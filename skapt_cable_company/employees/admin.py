"""
Module for Employee App Admin Pannel Integration
"""

from django.contrib import admin

from common.models import Employee

admin.site.register(Employee)
