# Generated by Django 5.1.7 on 2025-03-12 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freelancia_back_end', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='Address',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='Birthdate',
            new_name='birth_date',
        ),
    ]
