# Generated by Django 2.2.5 on 2021-06-30 04:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0028_auto_20210628_0700'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryaddress',
            name='social_media_handler',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]