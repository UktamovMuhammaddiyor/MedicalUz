# Generated by Django 4.0.5 on 2022-07-02 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_doctor_doctor_status_alter_doctor_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='username',
        ),
        migrations.AddField(
            model_name='botuser',
            name='first_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]
