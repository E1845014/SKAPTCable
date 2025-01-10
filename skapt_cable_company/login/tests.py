"""
Module for all the Login Related Test Cases
"""

# pylint: disable=imported-auth-user

from django.test import TestCase
from django.contrib.auth.models import User

from common.tests import BaseTestCase


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
    """
    Test Cases for testing the Logout functionality
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
    """
    Test Cases for testing the Home Page and their functionality
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


class ChangePasswordTestCase(BaseTestCase):
    """
    Test Cases for testing the Change Password functionality
    """

    def setUp(self):
        """
        Runs on Test Case Start up

        Contains Base Data needed for testing
        """
        self.raw_password = self.get_random_string(10)
        self.new_password = self.get_random_string(10)
        while self.new_password == self.raw_password:
            self.new_password = self.get_random_string(10)
        self.user = User.objects.create_user(
            username=self.get_random_string(10),
            email=f"{self.get_random_string()}@{self.get_random_string()}.com",
            password=self.raw_password,
        )
        self.client.login(username=self.user.username, password=self.raw_password)
        self.url = "/password"

    def test_change_password_renders(self):
        """
        Test whether Change Password Page Renders Correctly
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_password.html")

    def test_change_password_success(self):
        """
        Test whether user can successfully change password
        """
        response = self.client.post(
            self.url,
            {
                "old_password": self.raw_password,
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirects to home
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))

    def test_change_password_wrong_old_password(self):
        """
        Test whether wrong old password prevents changing password
        """
        response = self.client.post(
            self.url,
            {
                "old_password": "wrong_password",
                "new_password1": self.new_password,
                "new_password2": self.new_password,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_password.html")
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.new_password))

    def test_change_password_mismatch_new_passwords(self):
        """
        Test whether mismatched new passwords prevent changing password
        """
        response = self.client.post(
            self.url,
            {
                "old_password": self.raw_password,
                "new_password1": self.new_password,
                "new_password2": "different_new_password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("update_password.html")
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.new_password))
