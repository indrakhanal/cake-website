# Generated by Django 2.2.5 on 2021-03-12 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20210312_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]