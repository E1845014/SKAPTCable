# Generated by Django 4.2.7 on 2024-10-27 16:32

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0002_area_customer_alter_employee_phone_number_payment_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="area",
            name="collection_date",
            field=models.SmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(
                        0, "Has to be higher than zero"
                    ),
                    django.core.validators.MaxValueValidator(
                        30, "Has to be less than 30"
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="customer",
            name="connection_start_date",
            field=models.DateField(
                default=datetime.datetime(
                    2024, 10, 27, 16, 32, 33, 524134, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
