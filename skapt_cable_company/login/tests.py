from django.test import TestCase
from django.contrib.auth.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.raw_password = "top_secret"
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def test_login_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("index.html")

    def test_login_redirects_to_home_for_logged_in_users(self):
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get("/", follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("home.html")
        self.assertTemplateNotUsed("index.html")

    def test_login_can_login(self):
        response = self.client.post(
            "/", {"username": self.user.username, "password": self.raw_password}
        )
        self.assertEqual(response.status_code, 302)  ## Redirects
        self.assertTemplateUsed("home.html")

    def test_login_cant_login_with_wrong_cred(self):
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
        response = self.client.post("/", {"username": self.user.username})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("index.html")
        self.assertIn(
            {"message": "Invalid Parameters", "class_name": " is-danger"},
            response.context["notifications"],
        )


class LogoutTestCase(TestCase):
    def setUp(self):
        self.raw_password = "top_secret"
        self.user = User.objects.create_user(
            username="jacob", email="jacob@…", password=self.raw_password
        )

    def test_logout_works(self):
        self.client.login(username=self.user.username, password=self.raw_password)
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.has_key("_auth_user_id"))
        self.assertTemplateUsed("index.html")

    def test_logout_for_anon(self):
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)


# Create your tests here.