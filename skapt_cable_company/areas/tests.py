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

from .forms import AreaForm


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


class AddAreaTestCase(AreaBaseTestCase):
    """
    Test Cases for testing Add new Area Functionality and UI
    """

    def setUp(self):
        """
        Setup Add Area Testings
        """
        self.expected_form_fields = ["name", "agent"]
        self.url = "/areas/add"
        return super().setUp()

    def test_page_renders_for_admin_employees(self):
        """
        Test if the page only loads for employees and super admins
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_not_renders_for_non_admin_employee(self):
        """
        Test if the page not loads for non employees
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_not_renders_for_non_employee(self):
        """
        Test if the page not loads for non employees
        """
        non_employee_user = User.objects.create_user(
            "username", "email@mail.co", self.raw_password
        )
        non_employee_user.save()
        self.client.login(
            username=non_employee_user.username, password=self.raw_password
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_page_renders_form_superuser(self):
        """
        Test if the page only loads for super user
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_form_fields(self):
        """
        Test the fields passed in the form
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertIn("area_form", response.context)
        area_form: Form = response.context["area_form"]

        for expected_user_form_field in self.expected_form_fields:
            self.assertIn(expected_user_form_field, area_form.fields)

        self.assertTemplateUsed("add_areas.html")

    def test_form_submission(self):
        """
        Test the form submission on correct variables by employee
        """
        employees = self.generate_employees()
        employee = employees[0]
        employee.is_admin = True
        employee.save()
        self.login_as_employee(employee)
        get_response = self.client.get(self.url)
        area_form: Form = get_response.context["area_form"]
        agent_choices = area_form.fields["agent"].choices
        request_object = {}
        for field in self.expected_form_fields:
            if field == "agent":
                request_object[field] = list(agent_choices)[1][0]
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 302)
        new_area_query = Area.objects.filter(agent=employees[1])

        self.assertTrue(len(new_area_query) > 0)
        new_area = new_area_query[0]
        self.assertRedirects(response, f"/areas/{new_area.pk}")

    def test_form_submission_as_non_employee(self):
        """
        Test the form submission on correct variables by non employee
        """

        ## Get Choices first
        employees = self.generate_employees()
        area_form = AreaForm()
        agent_choices = area_form.fields["agent"].choices
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        request_object = {}
        for field in self.expected_form_fields:
            if field == "agent":
                request_object[field] = list(agent_choices)[1][0]
            else:
                request_object[field] = field
        response = self.client.post("/employees/add", request_object)
        self.assertEqual(response.status_code, 403)
        new_area_query = Area.objects.filter(agent=employees[1])
        self.assertTrue(len(new_area_query) == 0)

    def test_wrong_request_type(self):
        """
        Test whether other request types are supported
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 400)

    def test_errored_form_submission(self):
        """
        Test the form submission on incorrect variables
        """
        employees = self.generate_employees()
        employee = employees[0]
        employee.is_admin = True
        employee.save()
        self.login_as_employee(employee)
        request_object = {}
        for field in self.expected_form_fields:
            if field == "agent":
                request_object[field] = self.get_random_string(10)
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 200)
        new_area_query = Area.objects.filter(agent=employees[1])
        self.assertEqual(len(new_area_query), 0)
