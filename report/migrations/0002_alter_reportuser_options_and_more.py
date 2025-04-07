# Generated by Django 5.1.7 on 2025-04-06 23:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0008_alter_contract_unique_together'),
        ('report', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportuser',
            options={'verbose_name': 'User Report', 'verbose_name_plural': 'User Reports'},
        ),
        migrations.AddField(
            model_name='reportuser',
            name='resolution_reason',
            field=models.CharField(blank=True, choices=[('violation', 'Terms violation found'), ('no_violation', 'No violation found'), ('false', 'False report'), ('other', 'Other reason')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='reportuser',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reportuser',
            name='resolved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_resolved', to=settings.AUTH_USER_MODEL, verbose_name='Resolved by'),
        ),
        migrations.AddField(
            model_name='reportuser',
            name='resolved_notes',
            field=models.TextField(blank=True, help_text='Details about how this report was resolved', null=True),
        ),
        migrations.AlterField(
            model_name='reportuser',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='reportuser',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reports_made_on_users', to=settings.AUTH_USER_MODEL, verbose_name='Reporting User'),
        ),
        migrations.AlterField(
            model_name='reportuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_reports_received', to=settings.AUTH_USER_MODEL, verbose_name='Reported User'),
        ),
        migrations.CreateModel(
            name='ReportContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('resolved', 'Resolved'), ('ignored', 'Ignored')], default='pending', max_length=20)),
                ('resolved_notes', models.TextField(blank=True, help_text='Details about how this report was resolved', null=True)),
                ('resolution_reason', models.CharField(blank=True, choices=[('violation', 'Terms violation found'), ('no_violation', 'No violation found'), ('false', 'False report'), ('other', 'Other reason')], max_length=20, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract_reports_received', to='contract.contract', verbose_name='Reported Contract')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reports_made_on_contracts', to=settings.AUTH_USER_MODEL, verbose_name='Reporting User')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_resolved', to=settings.AUTH_USER_MODEL, verbose_name='Resolved by')),
            ],
            options={
                'verbose_name': 'Contract Report',
                'verbose_name_plural': 'Contract Reports',
                'abstract': False,
            },
        ),
    ]
