# Generated by Django 5.1.7 on 2025-03-25 05:09

import django.db.models.deletion
import payments.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_transaction_currency_transaction_payment_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='payment_method',
            field=models.ForeignKey(default=payments.models.Transaction.get_default_payment_method, on_delete=django.db.models.deletion.CASCADE, to='payments.paymentmethod'),
        ),
    ]
