"""
Module for all the Login Related Test Cases
"""

from django.test import TestCase
from django.contrib.auth.models import User


class LoginTestCase(TestCase):
    """
    Test Cases for testing the Login Page and their functionality
    """

    def setUp(self):
        """
        Runs on Test Case Start up

        Contains Base Data needed for testing
        """
        self.raw_password = "top_secret"
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def test_login_renders(self):
        """
        Test whether Login Page Renders Correctly
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("index.html")

    def test_login_redirects_to_home_for_logged_in_users(self):
        """
        Tests whether successfull login allow users to access home page
        """
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("home.html")
        self.assertTemplateNotUsed("index.html")

    def test_login_can_login(self):
        """
        Test whether user can login redirects to home page
        """
        response = self.client.post(
            "/", {"username": self.user.username, "password": self.raw_password}
        )
        self.assertEqual(response.status_code, 302)  ## Redirects
        self.assertTemplateUsed("home.html")

    def test_login_cant_login_with_wrong_cred(self):
        """
        Check if wrong credentials prevent login
        """
        response = self.client.post(
            "/", {"username": self.user.username, "password": f"{self.raw_password}123"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("index.html")
        self.assertIn(
            {"message": "Wrong Username or Password", "class_name": " is-danger"},
            response.context["notifications"],
        )

    def test_login_missing_data(self):
        """
        Check if missing data prevents login
        """
        response = self.client.post("/", {"username": self.user.username})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("index.html")
        self.assertIn(
            {"message": "Invalid Parameters", "class_name": " is-danger"},
            response.context["notifications"],
        )


class LogoutTestCase(TestCase):
    def setUp(self):
        """
        Runs on Test Case Start up

        Contains Base Data needed for testing
        """
        self.raw_password = "top_secret"
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def test_logout_works(self):
        """
        Checks whether logout works
        """
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.has_key("_auth_user_id"))
        self.assertTemplateUsed("index.html")

    def test_logout_for_anon(self):
        """
        Checks if unlogin user logout he got 302 status code
        """
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)


class HomeTestCase(TestCase):
    def setUp(self):
        """
        Runs on Test Case Start up

        Contains Base Data needed for testing
        """
        self.raw_password = "top_secret"
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def test_only_support_get_request(self):
        """
        Check whether home page only accepts get request
        """
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get("/home")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("home.html")
        response = self.client.post("/home")
        self.assertEqual(response.status_code, 400)


# Create your tests here.
