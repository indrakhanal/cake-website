# Generated by Django 2.2.5 on 2021-06-20 06:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0016_auto_20210620_0632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vendor', to='sales.Vendor'),
        ),
        migrations.AlterField(
            model_name='orderdelivery',
            name='factory',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='factory_delivery_order', to='sales.Factory'),
        ),
    ]