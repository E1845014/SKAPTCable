"""
Module to contain all Customers App View Controller Codes
"""

# pylint: disable=imported-auth-user

from datetime import date

from django.contrib.auth.models import User
from django.forms import Form

from common.tests import BaseTestCase
from common.models import Customer, Area, CustomerConnection


class CustomerBaseTestCase(BaseTestCase):
    """
    Bese Tast Functionalities for Customer App Testing
    """


class CustomersTestCase(CustomerBaseTestCase):
    """
    Test Cases for testing Customers List Page and their functionalities
    """

    def test_page_renders_for_employees(self):
        """
        Test if the customers page renders for employee user
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("customers.html")
        self.client.logout()
        response = self.client.get("/customers/")
        self.assertNotEqual(response.status_code, 200)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the customers page not renders for non-employees
        """
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.get("/customers/")
        self.assertEqual(response.status_code, 403)

    def test_shows_all_customers(self):
        """
        Test if all the employees are shown
        """
        customers = self.generate_customers()
        self.login_as_employee(customers[0].area.agent)
        response = self.client.get("/customers/")
        self.assertEqual(len(response.context["customers"]), len(customers))

    def test_other_request_method(self):
        """
        Test if the customers page not renders for any other request than GET
        """
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.post("/customers/")
        self.assertNotEqual(response.status_code, 200)

    def test_customer_size(self):
        """
        Test if can filter customers based on the size of the list
        """
        self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_size = 1
        response = self.client.get("/customers/", {"size": request_size})
        self.assertEqual(len(response.context["customers"]), request_size)

    def test_page_number(self):
        """
        Test if can filter customers based on the page number
        """
        self.generate_customers(20)
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        page_number = 2
        response = self.client.get("/customers/", {"page": page_number})
        self.assertEqual(response.context["customers"].number, page_number)

    def test_non_numeric_params(self):
        """
        Test if can filter customers with wrong queries
        """
        self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        request_size = self.get_random_string()
        page_number = self.get_random_string()
        response = self.client.get(
            "/customers/", {"page": page_number, "size": request_size}
        )
        self.assertNotEqual(len(response.context["customers"]), request_size)
        self.assertNotEqual(response.context["customers"].number, page_number)

    def test_search_text(self):
        """
        Test if can filter customer with search text
        """
        customers = self.generate_customers()
        employee = self.generate_employees(1)[0]
        self.login_as_employee(employee)
        response = self.client.get(
            "/customers/", {"search_text": customers[0].identity_no}
        )
        self.assertEqual(response.context["customers"][0].pk, customers[0].pk)


class AddCustomerTestCase(CustomerBaseTestCase):
    """
    Test Cases for testing Add Customer functionalities
    """

    def setUp(self):
        """
        Setup Add Add Customer Testings
        """
        super().setUp()
        self.url = "/customers/add"
        self.expected_user_form_fields = ["first_name", "last_name", "email"]
        self.expected_form_fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "connection_start_date",
            "area",
        ]
        self.areas = self.generate_areas()

    def test_page_renders_for_admin_employees(self):
        """
        Test if the page loads for admin employees
        """
        employee = self.areas[0].agent
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_not_renders(self):
        """
        Test if the add Customer Page not renders for selected user groups
        """
        self.helper_non_render_test(self.url, True, True)

    def test_page_renders_for_superuser(self):
        """
        Test if the Add Customer page renders for super users
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_redirects_when_no_area(self):
        """
        Test if the page redirects when there is no area
        """
        Area.objects.all().delete()
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_form_fields(self):
        """
        Test the fields pased in the form
        """
        employee = self.areas[0].agent
        self.login_as_employee(employee, True)
        response = self.client.get(self.url)
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]
        for expected_user_form_field in self.expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("customer_form", response.context)
        customer_form: Form = response.context["customer_form"]

        for expected_customer_form_field in self.expected_form_fields:
            self.assertIn(expected_customer_form_field, customer_form.fields)
        self.assertTemplateUsed("add_employees.html")

    def test_post_request(self):
        """
        Test the form submission on correct variables
        """
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email@email.com"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_form_submission_as_non_employee(self):
        """
        Test the form submission on correct variables
        """
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email@email.com"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        self.client.logout()
        user = User.objects.create_user(
            "username", "email@email.email", self.raw_password
        )
        self.client.login(username=user.username, password=self.raw_password)
        response = self.client.post(self.url, request_object)
        self.assertEqual(response.status_code, 403)
        new_employee_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertTrue(len(new_employee_query) == 0)

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
        area = self.areas[0]
        employee = area.agent
        self.login_as_employee(employee, True)
        get_response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = self.get_random_phone_number()
        user_form: Form = get_response.context["user_form"]
        customer_form: Form = get_response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        for field in user_form.fields:
            if field == "email":
                request_object[field] = "email"
            else:
                request_object[field] = field
        for field in customer_form.fields:
            if field == "area":
                request_object[field] = list(area_choices)[1][0]
            elif field == "phone_number":
                request_object[field] = new_customer_phone_number
            elif field == "connection_start_date":
                request_object[field] = date.today()
            else:
                request_object[field] = field
        response = self.client.post(self.url, request_object)
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertEqual(len(new_customer_query), 0)
        self.assertEqual(response.status_code, 200)


class ViewCustomerTestCase(CustomerBaseTestCase):
    """
    Test cases for view Customer Page View Controller
    """

    def setUp(self):
        """
        Setup View Customer Testings
        """
        super().setUp()
        self.customer = self.generate_customers(1)[0]
        self.url = f"/customers/{self.customer.user.pk}"
        self.expected_user_form_fields = ["first_name", "last_name", "email"]
        self.expected_form_fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "connection_start_date",
            "area",
        ]

    def test_page_renders(self):
        """
        Test if the page renders and using correct template
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("customer.html")

    def test_self_page_renders(self):
        """
        Test if the page renders for customers to view their profile
        """
        self.login_as_customer(self.customer)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_renders_for_admins(self):
        """
        Test if the page renders for admins to view other customers
        """
        self.login_as_employee(self.generate_employees(1)[0], True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_renders_for_employees(self):
        """
        Test if the page renders for admins to view customers
        """
        self.login_as_employee(self.generate_employees(1)[0])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_not_renders_for_non_employees(self):
        """
        Test if the page not renders for non-employees for any customers
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_data_fields(self):
        """
        Test whether expected datas are passed
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]

        for expected_user_form_field in self.expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("customer_form", response.context)
        customer_form: Form = response.context["customer_form"]

        for expected_customer_form_field in self.expected_form_fields:
            self.assertIn(expected_customer_form_field, customer_form.fields)

    def test_non_exist_customer(self):
        """
        Test whether page handles not existing customer search
        """
        pk = str(self.customer.user.pk)
        while Customer.objects.filter(pk=pk).exists():
            pk += self.get_random_phone_number()
        self.login_as_superuser()
        response = self.client.get(f"/customers/{pk}")
        self.assertEqual(response.status_code, 404)


class UpdateCustomerTestCase(CustomerBaseTestCase):
    """
    Testcase for Update Customer UI and Functionality
    """

    def setUp(self):
        """
        Setup View Customer Testings
        """
        super().setUp()
        self.customer = self.generate_customers(1)[0]
        self.url = f"/customers/{self.customer.user.pk}/update"
        self.expected_user_form_fields = ["first_name", "last_name", "email"]
        self.expected_form_fields = [
            "phone_number",
            "address",
            "identity_no",
            "box_ca_number",
            "active_connection",
            "has_digital_box",
            "offer_power_intake",
            "connection_start_date",
            "area",
        ]

    def test_page_renders(self):
        """
        Test if the page renders
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_customer.html")

    def test_non_employee_page_not_renders(self):
        """
        Test if the page not renders for non-employees for any customers
        """
        self.login_as_non_employee()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_data_fields(self):
        """
        Test whether expected datas are passed
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        self.assertIn("user_form", response.context)
        user_form: Form = response.context["user_form"]

        for expected_user_form_field in self.expected_user_form_fields:
            self.assertIn(expected_user_form_field, user_form.fields)
        self.assertIn("customer_form", response.context)
        customer_form: Form = response.context["customer_form"]

        for expected_customer_form_field in self.expected_form_fields:
            self.assertIn(expected_customer_form_field, customer_form.fields)

    def test_update_customer_as_super_user(self):
        """
        Test whether super user can update customer
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_update_customer_area(self):
        """
        Test whether Employee can update customer area
        """
        self.login_as_employee(self.generate_employees(1)[0], True)
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        area_choices = customer_form.fields["area"].choices
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        request_object["area"] = list(area_choices)[3][0]
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_update_customer_as_admin(self):
        """
        Test whether Employee can update customer
        """
        self.login_as_employee(self.generate_employees(1)[0], True)
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_update_customer_by_their_agent(self):
        """
        Test whether agent can update their customer
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertGreater(len(new_customer_query), 0)
        new_customer = new_customer_query[0]
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/customers/{new_customer.user.pk}")

    def test_update_customer_by_not_agent(self):
        """
        Test whether Employee cannot update customer
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        self.login_as_employee(self.generate_employees(1)[0])
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertFalse(new_customer_query.exists())
        self.assertEqual(response.status_code, 403)

    def test_non_employee_not_update_any_areas(self):
        """
        Test the form submission as non employee failing
        """
        self.login_as_superuser()
        response = self.client.get(self.url)
        request_object = {}
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        self.login_as_non_employee()
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )
        new_customer_query = Customer.objects.filter(
            phone_number=new_customer_phone_number
        )
        self.assertFalse(new_customer_query.exists())
        self.assertEqual(response.status_code, 403)

    def test_invalid_data(self):
        """
        Test whether invalid data is handled
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        new_customer_phone_number = "0771234458"
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        request_object["phone_number"] = new_customer_phone_number
        request_object["area"] = self.get_random_string()
        response = self.client.post(
            f"/customers/{self.customer.pk}/update", request_object
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_customer.html")

        area_form: Form = response.context["customer_form"]
        self.assertFalse(area_form.is_valid())

        new_area_query = Customer.objects.filter(phone_number=new_customer_phone_number)
        self.assertEqual(len(new_area_query), 0)

    def test_wrong_request_type(self):
        """
        Test whether other request types are supported
        """
        self.login_as_employee(self.customer.agent)
        response = self.client.get(self.url)
        user_form: Form = response.context["user_form"]
        customer_form: Form = response.context["customer_form"]
        request_object = {**user_form.initial, **customer_form.initial}
        response = self.client.put(self.url, request_object)
        self.assertEqual(response.status_code, 400)


class ConnectionTestCase(CustomerBaseTestCase):

    def setUp(self):
        """
        Setup View Customer Testings
        """
        super().setUp()
        self.customer = self.generate_customers(1)[0]

    def test_add_connection(self):
        """
        Test if new connections can be added
        """
        url = f"/customers/{self.customer.user.pk}/addConnection"
        self.login_as_employee(self.customer.agent)
        self.client.get(url)
        self.assertGreater(
            CustomerConnection.objects.filter(customer=self.customer).count(), 0
        )

    def test_enable_connection(self):
        """
        Test if disabled connection can be enabled
        """
        self.login_as_employee(self.customer.agent)
        connection = CustomerConnection(customer=self.customer, active=False)
        connection.save()
        self.assertFalse(connection.active)
        url = f"/customers/{self.customer.user.pk}/{connection.pk}/enableConnection"
        self.client.get(url)
        self.assertTrue(CustomerConnection.objects.get(pk=connection.pk).active)
        connection.active = False
        connection.save()
        self.login_as_non_employee()
        self.client.get(url)
        self.assertFalse(CustomerConnection.objects.get(pk=connection.pk).active)

    def test_disable_connection(self):
        """
        Test if enable connection can be disabled
        """
        self.login_as_employee(self.customer.agent)
        connection = CustomerConnection(customer=self.customer)
        connection.save()
        self.assertTrue(connection.active)
        url = f"/customers/{self.customer.user.pk}/{connection.pk}/disableConnection"
        self.client.get(url)
        self.assertFalse(CustomerConnection.objects.get(pk=connection.pk).active)
        connection.active = True
        connection.save()
        self.login_as_non_employee()
        self.client.get(url)
        self.assertTrue(CustomerConnection.objects.get(pk=connection.pk).active)
