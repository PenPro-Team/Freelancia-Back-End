# Generated by Django 5.1.7 on 2025-04-05 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0004_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='file',
            field=models.FileField(upload_to='contract_attachments/'),
        ),
    ]
