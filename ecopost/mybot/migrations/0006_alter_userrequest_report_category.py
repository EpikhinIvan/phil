# Generated by Django 4.2.7 on 2024-05-07 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mybot', '0005_alter_userrequest_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrequest',
            name='report_category',
            field=models.CharField(max_length=255, verbose_name='Категория'),
        ),
    ]
