# Generated by Django 4.0.5 on 2022-07-22 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0028_doctor_unique_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='doctor_id',
            field=models.CharField(default='', max_length=255),
        ),
    ]
