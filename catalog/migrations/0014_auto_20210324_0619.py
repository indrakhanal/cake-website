# Generated by Django 2.2.5 on 2021-03-24 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_merge_20210321_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributevalue',
            name='attribute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute', to='catalog.Attribute'),
        ),
    ]