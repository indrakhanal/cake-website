# Generated by Django 2.2.5 on 2021-06-20 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0015_auto_20210620_0606'),
    ]

    operations = [
        migrations.CreateModel(
            name='Factory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Factory',
                'ordering': ('-id',),
            },
        ),
        migrations.AddField(
            model_name='orderdelivery',
            name='factory',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='factory_delivery_order', to='sales.Factory'),
        ),
    ]