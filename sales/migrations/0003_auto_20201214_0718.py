# Generated by Django 2.2 on 2020-12-14 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_auto_20201206_1253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='customer_notes',
        ),
        migrations.RemoveField(
            model_name='order',
            name='refunded_amount',
        ),
    ]