# Generated by Django 4.2.7 on 2024-05-06 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybot', '0004_alter_userrequest_location_lat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrequest',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время создания'),
        ),
    ]