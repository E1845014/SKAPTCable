"""
Module That provide common utility functions
"""

from django.http import HttpRequest


def pagination_handle(request: HttpRequest):
    size = request.GET.get("size", "10")
    if size.isnumeric():
        size = int(size)
    else:
        size = 10
    page_number = request.GET.get("page", "1")
    if page_number.isnumeric():
        page_number = int(page_number)
    else:
        page_number = 1
    return size, page_number
