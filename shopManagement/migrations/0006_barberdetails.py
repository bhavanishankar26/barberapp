# Generated by Django 3.2.8 on 2024-09-26 16:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shopManagement', '0005_alter_shopprofile_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='BarberDetails',
            fields=[
                ('barber_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('barber_name', models.CharField(max_length=70)),
                ('phone_number', models.CharField(max_length=15)),
                ('shop_profile', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='barber_details', to='shopManagement.shopprofile')),
            ],
        ),
    ]
