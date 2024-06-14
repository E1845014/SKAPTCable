from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import login, logout, authenticate

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
                return
            errors.append("Wrong Username or Password")
        errors.append("Invalid Parameters")
    else:
        form = LoginForm()
    return HttpResponse(template.render({"form": form}, request))


# Create your views here.
