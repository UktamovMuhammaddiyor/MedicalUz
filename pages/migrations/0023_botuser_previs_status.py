# Generated by Django 4.0.5 on 2022-07-07 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0022_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='previs_status',
            field=models.CharField(default='', max_length=255),
        ),
    ]
