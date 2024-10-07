# Generated by Django 3.2.8 on 2024-09-14 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopManagement', '0002_auto_20240902_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopprofile',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='shopprofile',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=9, null=True),
        ),
    ]
