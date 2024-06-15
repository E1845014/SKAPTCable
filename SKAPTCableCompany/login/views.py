from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import BadRequest
from django.shortcuts import redirect

from .forms import LoginForm


def index(request):
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
        errors.append("Invalid Parameters")
    else:
        form = LoginForm()
    return HttpResponse(template.render({"form": form}, request))


@login_required
def home(request):
    template = loader.get_template("home.html")
    if request.method == "GET":
        return HttpResponse(template.render({}, request))
    else:
        raise BadRequest


# Create your views here.
