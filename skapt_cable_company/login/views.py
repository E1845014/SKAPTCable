"""
Module to contain all Login App View Controller Codes
"""

from django.http import HttpResponse, HttpRequest
from django.template import loader
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.shortcuts import redirect
from .forms import LoginForm


def index(request: HttpRequest):
    """
    Login Page View Controller
    """
    template = loader.get_template("index.html")
    errors = []
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=request.POST["username"],
                password=request.POST["password"],
            )
            if user is not None:
                login(request, user)
                return redirect("/home")
            errors.append("Wrong Username or Password")
        else:
            errors.append("Invalid Parameters")
    else:
        if request.user.is_authenticated is True:
            return redirect("/home")
        form = LoginForm()
    return HttpResponse(
        template.render(
            {
                "form": form,
                "notifications": [
                    {"message": error, "class_name": " is-danger"} for error in errors
                ],
            },
            request,
        )
    )


@login_required
def home(request: HttpRequest):
    """
    Home Page View Controller
    """
    template = loader.get_template("home.html")
    if request.method == "GET":
        return HttpResponse(template.render({}, request))
    raise BadRequest


@login_required
def logout_user(request: HttpRequest):
    """
    Logout Controller
    """
    logout(request)
    return redirect("/")


# Create your views here.
