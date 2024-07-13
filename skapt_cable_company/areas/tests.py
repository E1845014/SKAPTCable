"""
Module for all Area Tests
"""

from time import time
from typing import List

from django.test import TestCase
from django.contrib.auth.models import User
from django.forms import Form


from common.models import Employee, Area
from common.tests import BaseTestCase


class AreaBaseTestCase(BaseTestCase):
    """
    Base Test Functionalities for Area App Testings
    """


class AreasTestCase(AreaBaseTestCase):
    """
    Test Cases for testing Areas List Page and their functionality
    """

    def test_page_renders_for_employee(self):
        """
        Test if the areas page renders for employee user
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get("/areas/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("areas.html")
        self.client.logout()
        response = self.client.get("/areas/")
        self.assertNotEqual(response.status_code, 200)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the areas page not renders for non-employees
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.get("/areas/")
        self.assertEqual(response.status_code, 403)

    def test_shows_all_areas(self):
        """
        Test if all the employees are shown
        """
        employees = self.generate_employees()
        areas = self.generate_areas(employees=employees)
        self.login_as_employee(employees[0])
        response = self.client.get("/areas/")
        self.assertEqual(len(response.context["areas"]), len(areas))
