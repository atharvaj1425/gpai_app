# Generated by Django 5.1.3 on 2024-11-29 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpai_app', '0005_alter_image_waste_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
