"""
Module That provide common utility functions
"""

from django.http import HttpRequest


def pagination_handle(request: HttpRequest, default_size=10, default_page_number=1):
    size = request.GET.get("size", str(default_size))
    if size.isnumeric():
        size = int(size)
    else:
        size = default_size
    page_number = request.GET.get("page", str(default_page_number))
    if page_number.isnumeric():
        page_number = int(page_number)
    else:
        page_number = default_page_number
    return size, page_number
