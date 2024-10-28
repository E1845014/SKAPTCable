"""
Module for all Area Tests
"""

# pylint: disable=imported-auth-user

from django.contrib.auth.models import User
from django.forms import Form


from common.models import Area
from common.tests import BaseTestCase

from .forms import AreaForm


class AreaBaseTestCase(BaseTestCase):
    """
    Base Test Functionalities for Area App Testings
    """

    def setUp(self):
        """
        Setup Class for All Area Related Test Cases
        """
        self.expected_form_fields = ["name", "agent", "collection_date"]
        return super().setUp()


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

    def test_page_not_renders(self):
        """
        Test if the Add Area Page not renders for selected user groups
        """
        self.helper_non_render_test(self.url, True, True)

    def test_page_renders_form_superuser(self):
        """
        Test if the Add Area page loads for super user
        """
        self.generate_employees()
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_when_no_employee(self):
        """
        Test if the page redirects when there is no employees
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_form_fields(self):
        """
        Test the fields passed in the form
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertIn("area_form", response.context)
        area_form: Form = response.context["area_form"]

        for expected_form_field in self.expected_form_fields:
            self.assertIn(expected_form_field, area_form.fields)

        self.assertTemplateUsed("add_areas.html")

    def test_form_submission(self):
        """
        Test the form submission on correct variables by employee
        """
        employees = self.generate_employees()
        employee = employees[0]
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        area_form: Form = get_response.context["area_form"]
        agent_choices = area_form.fields["agent"].choices
        request_object = {}
        for field in self.expected_form_fields:
            if field == "agent":
                request_object[field] = list(agent_choices)[1][0]
            elif field == "collection_date":
                request_object[field] = 1
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 302)
        new_area_query = Area.objects.filter(name="name")

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
            elif field == "collection_date":
                request_object[field] = 1
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
        self.login_as_employee(employee, True)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, 400)

    def test_errored_form_submission(self):
        """
        Test the form submission on incorrect variables
        """
        employees = self.generate_employees()
        employee = employees[0]
        self.login_as_employee(employee, True)
        request_object = {}
        for field in self.expected_form_fields:
            if field == "agent":
                request_object[field] = self.get_random_string(10)
            elif field == "collection_date":
                request_object[field] = 1
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 200)
        new_area_query = Area.objects.filter(agent=employees[1])
        self.assertEqual(len(new_area_query), 0)


class ViewAreaTestCase(AreaBaseTestCase):
    """
    Test Cases for testing view Area Page controller
    """

    def test_page_renders(self):
        """
        Test if the page renders and using correct template
        """
        employees = self.generate_employees()
        areas = self.generate_areas(employees=employees)
        self.login_as_superuser()
        response = self.client.get(f"/areas/{areas[0].pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("area.html")

    def test_employee_can_see_their_area(self):
        """
        Test if an employee can view the area under their service
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees=employees)[0]
        self.login_as_employee(area.agent)
        response = self.client.get(f"/areas/{area.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("area.html")

    def test_admin_can_see_any_area(self):
        """
        Test if an employee can view the area under their service
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees=employees[1:])[
            0
        ]  ## Create an Area where the first employee cannot be the agent
        employee = employees[0]
        self.login_as_employee(employee, True)
        response = self.client.get(f"/areas/{area.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("area.html")

    def test_non_admin_employee_cannot_see_other_areas(self):
        """
        Test if a non admin employee cannot see areas under their control
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees=employees[1:])[
            0
        ]  ## Create an Area where the first employee cannot be the agent
        employee = employees[0]
        self.login_as_employee(employee)
        response = self.client.get(f"/areas/{area.pk}")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("area.html")

    def test_non_employee_cannot_see_any_area(self):
        """
        Test if a non admin employee cannot see areas under their control
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees=employees)[0]
        new_user = User.objects.create_user(
            "username", "email@email.com", self.raw_password
        )
        self.client.login(username=new_user.username, password=self.raw_password)
        response = self.client.get(f"/areas/{area.pk}")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("area.html")

    def test_data_fields(self):
        """
        Test whether expected datas are passed
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees=employees)[0]
        self.login_as_employee(area.agent)
        response = self.client.get(f"/areas/{area.pk}")
        self.assertIn("area_form", response.context)
        area_form: Form = response.context["area_form"]
        for expected_form_field in self.expected_form_fields:
            self.assertIn(expected_form_field, area_form.fields)

    def test_not_exist_area(self):
        """
        Test whether page handles not existing area search
        """
        areas = self.generate_areas()
        self.login_as_employee(areas[0].agent, True)
        response = self.client.get(f"/areas/{len(areas)+1}")
        self.assertEqual(response.status_code, 404)


class UpdateAreaTestCase(AreaBaseTestCase):
    """
    Testcase for Update Area UI and Functionlity
    """

    def get_url(self, area: Area):
        """
        Generate Update Area URL for a given area
        """
        return f"/areas/{area.pk}/update"

    def generate_response(self, area: Area):
        """
        Generate Update Area GET Response for a given area
        """
        return self.client.get(self.get_url(area))

    def get_initial_values(self, area: Area):
        """
        Generate Initial Values of an Area that has to be used in the Update POST Request
        """
        self.login_as_employee(area.agent)
        response = self.generate_response(area)
        area_form: Form = response.context["area_form"]
        return {**area_form.initial}

    def test_page_renders(self):
        """
        Test if the page renders
        """
        areas = self.generate_areas()
        self.login_as_superuser()
        response = self.generate_response(areas[0])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_employee.html")

    def test_non_employee_page_not_renders(self):
        """
        Test if the page not renders for non-employees for any area
        """
        areas = self.generate_areas()
        new_user = User.objects.create_user(
            "username", "email@email.com", self.raw_password
        )
        self.client.login(username=new_user.username, password=self.raw_password)
        response = self.generate_response(areas[0])
        self.assertEqual(response.status_code, 403)

    def test_data_fields(self):
        """
        Test whether expected datas are passed
        """
        area = self.generate_areas(1)[0]
        self.login_as_employee(area.agent)
        response = self.generate_response(area)
        self.assertIn("area_form", response.context)
        area_form: Form = response.context["area_form"]
        for expected_form_field in self.expected_form_fields:
            self.assertIn(expected_form_field, area_form.fields)

    def test_update_area_as_super_user(self):
        """
        Test whether super user can update area
        """
        area = self.generate_areas(1)[0]
        self.login_as_superuser()
        response = self.generate_response(area)
        area_form: Form = response.context["area_form"]
        request_object = {**area_form.initial}
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        response = self.client.post(self.get_url(area), request_object)
        self.assertEqual(response.status_code, 302)
        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertGreater(len(new_area_query), 0)
        self.assertRedirects(response, f"/areas/{new_area_query[0].pk}")

    def test_update_area_as_admin(self):
        """
        Test whether Admin Employee can update area
        """
        employees = self.generate_employees()
        areas = self.generate_areas(employees=employees[1:])
        admin_employee = employees[0]
        self.login_as_employee(admin_employee, True)
        response = self.generate_response(areas[0])
        area_form: Form = response.context["area_form"]
        request_object = {**area_form.initial}
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        response = self.client.post(self.get_url(areas[0]), request_object)
        self.assertEqual(response.status_code, 302)
        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertGreater(len(new_area_query), 0)
        self.assertRedirects(response, f"/areas/{new_area_query[0].pk}")

    def test_update_area_by_its_agent(self):
        """
        Test whether employee can update their area
        """
        employees = self.generate_employees()
        areas = self.generate_areas(employees=employees)
        request_object = self.get_initial_values(areas[0])
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        response = self.client.post(self.get_url(areas[0]), request_object)
        self.assertEqual(response.status_code, 302)
        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertGreater(len(new_area_query), 0)
        self.assertRedirects(response, f"/areas/{new_area_query[0].pk}")

    def test_non_admin_employee_not_update_other_area(self):
        """
        Test whether non-admin Employees can't update other employees' areas
        """
        employees = self.generate_employees()
        area = self.generate_areas(1, employees[1:])[0]
        employee = employees[0]
        request_object = self.get_initial_values(area)
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        self.login_as_employee(employee)
        response = self.client.post(self.get_url(area), request_object)
        self.assertEqual(response.status_code, 403)
        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertEqual(len(new_area_query), 0)

    def test_non_employee_not_update_any_areas(self):
        """
        Test whether non Employees can't update any areas
        """
        area = self.generate_areas()[0]
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        request_object = self.get_initial_values(area)
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.post(self.get_url(area), request_object)
        self.assertEqual(response.status_code, 403)
        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertEqual(len(new_area_query), 0)

    def test_invalid_data(self):
        """
        Test whether invalid data is handled
        """
        area = self.generate_areas()[0]
        self.login_as_superuser()
        request_object = self.get_initial_values(area)

        request_object["agent"] = self.get_random_string(10)
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name

        response = self.client.post(self.get_url(area), request_object)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_area.html")

        area_form: Form = response.context["area_form"]
        self.assertFalse(area_form.is_valid())

        new_area_query = Area.objects.filter(name=new_area_name)
        self.assertEqual(len(new_area_query), 0)

    def test_wrong_request_type(self):
        """
        Test whether other request types are supported
        """
        employees = self.generate_employees()
        areas = self.generate_areas(employees=employees)
        request_object = self.get_initial_values(areas[0])
        new_area_name = self.get_random_string()
        request_object["name"] = new_area_name
        response = self.client.put(self.get_url(areas[0]), request_object)
        self.assertEqual(response.status_code, 400)
