from django.http import HttpRequest


def user_logged_in(request: HttpRequest):
    return {"user_is_authenticated": request.user.is_authenticated}
