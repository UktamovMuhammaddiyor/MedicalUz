# Generated by Django 4.0.5 on 2022-07-06 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0021_alter_doctor_home_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('username', models.CharField(max_length=255)),
            ],
        ),
    ]
