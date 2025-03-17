from rest_framework import serializers
from .models import Transaction, PaymentMethod
from django.core.exceptions import ValidationError

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    client_vat_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    freelancer_vat_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    final_amount = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    total_amount_with_vat = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)

    class Meta:
        model = Transaction
        fields = [
            'id', 'contract_client', 'contract_freelancer', 'contract_project',
            'contract_budget', 'payment_method', 'amount', 'state',
            'client_vat_amount', 'freelancer_vat_amount', 'final_amount',
            'total_amount_with_vat', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """
        Check that the transaction data is valid
        """
        if data['amount'] <= 0:
            raise ValidationError("Amount must be greater than zero")
        
        # Validate contract state
        if data['contract_client'].contract_state != 'aproved':
            raise ValidationError("Contract must be approved")
        
        return data