# Generated by Django 4.2.7 on 2024-07-13 10:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0002_alter_employee_phone_number_area"),
    ]

    operations = [
        migrations.AlterField(
            model_name="area",
            name="name",
            field=models.CharField(max_length=50),
        ),
    ]