# Generated by Django 4.0.5 on 2022-07-04 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0017_alter_doctor_city_alter_doctor_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='city',
            field=models.CharField(default='', max_length=255),
        ),
    ]