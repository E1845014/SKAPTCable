"""
Module to contain all Customer Model Related Functions
"""

from common.models import Customer


def generate_customer_number(customer: Customer, force=False):
    if customer.customer_number == "" or force:
        area = customer.area
        number_of_customers_in_the_area = Customer.objects.filter(area=area).count()
        return f"{area.name[:3]}{number_of_customers_in_the_area + 1}"
    raise Exception("Customer Number already Exists")
