"""
Module to contain all Customer Model Related Functions
"""

from common.models import Customer

def generate_customer_number(customer: Customer):
    if customer.customer_number == "":
        area = customer.area
        number_of_customers_in_the_area = Customer.objects.filter(area = area).count()
        return f"{area.name[:3]}{number_of_customers_in_the_area + 1}"
    return customer.customer_number