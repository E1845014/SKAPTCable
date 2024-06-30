"""
Module to include all Login Related Template Context Preprocessing
"""

from django.http import HttpRequest


def user_logged_in(request: HttpRequest):
    """
    method to check if the user is logged in
    """
    return {"user_is_authenticated": request.user.is_authenticated}
