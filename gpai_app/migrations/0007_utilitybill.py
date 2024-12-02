# Generated by Django 5.1.3 on 2024-12-01 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpai_app', '0006_alter_image_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='UtilityBill',
            fields=[
                ('bill_id', models.AutoField(primary_key=True, serialize=False)),
                ('month_year', models.CharField(help_text='Format: MM-YYYY', max_length=7)),
                ('electricity_units_consumed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Electricity Units Consumed')),
                ('electricity_bill_amount', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='Electricity Bill Amount')),
                ('water_units_consumed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Water Units Consumed')),
                ('water_bill_amount', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='Water Bill Amount')),
                ('post_office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='utility_bills', to='gpai_app.postoffice')),
            ],
            options={
                'verbose_name': 'Utility Bill',
                'verbose_name_plural': 'Utility Bills',
                'unique_together': {('post_office', 'month_year')},
            },
        ),
    ]
