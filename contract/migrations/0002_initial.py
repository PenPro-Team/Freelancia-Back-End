# Generated by Django 5.1.7 on 2025-03-14 19:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contract', '0001_initial'),
        ('freelancia_back_end', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contract',
            name='freelancer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='freelancer', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contract',
            name='project',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='freelancia_back_end.project'),
        ),
        migrations.AlterUniqueTogether(
            name='contract',
            unique_together={('freelancer', 'client', 'project')},
        ),
    ]
