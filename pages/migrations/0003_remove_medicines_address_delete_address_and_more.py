# Generated by Django 4.0.5 on 2022-07-02 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_rename_name_medicines_medicine_name_address_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medicines',
            name='address',
        ),
        migrations.DeleteModel(
            name='Address',
        ),
        migrations.DeleteModel(
            name='Medicines',
        ),
    ]
