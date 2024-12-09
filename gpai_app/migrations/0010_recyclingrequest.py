# Generated by Django 5.1.3 on 2024-12-03 09:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpai_app', '0009_campaign_drive_venue'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecyclingRequest',
            fields=[
                ('recycle_id', models.AutoField(primary_key=True, serialize=False)),
                ('name_of_recycler', models.CharField(max_length=255)),
                ('phone_no', models.CharField(max_length=15)),
                ('recycle_item', models.CharField(max_length=255)),
                ('num_of_items', models.PositiveIntegerField()),
                ('quantity_to_recycle', models.FloatField()),
                ('pincode', models.CharField(max_length=6)),
                ('post_office_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gpai_app.postoffice')),
            ],
        ),
    ]