# Generated by Django 5.1.7 on 2025-03-23 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='contract_state',
            field=models.CharField(choices=[('pending', 'Pending'), ('aproved', 'Aproved'), ('canceled', 'Canceled'), ('finished', 'Finished'), ('hold', 'Hold')], default='pending', max_length=20),
        ),
    ]
