# Generated by Django 5.1.3 on 2024-11-25 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gpai_app', '0002_divisionaloffice_alter_postoffice_division'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='divisionaloffice',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='divisionaloffice',
            name='longitude',
        ),
        migrations.RemoveField(
            model_name='divisionaloffice',
            name='region',
        ),
    ]
