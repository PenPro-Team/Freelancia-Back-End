# Generated by Django 5.1.7 on 2025-03-20 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freelancia_back_end', '0005_certificate'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='attachments/'),
        ),
    ]
