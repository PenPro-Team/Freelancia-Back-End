# Generated by Django 5.1.7 on 2025-03-14 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freelancia_back_end', '0006_alter_project_project_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='skills',
            field=models.ManyToManyField(related_name='projects', to='freelancia_back_end.skill'),
        ),
    ]
