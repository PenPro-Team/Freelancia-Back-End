from rest_framework import serializers
from .models import Transaction, PaymentMethod, Withdrawal
from django.core.exceptions import ValidationError
from freelancia_back_end.serializers import AdminPublicUserSerializer


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    client_vat_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2)
    freelancer_vat_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2)
    final_amount = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2)
    total_amount_with_vat = serializers.DecimalField(
        read_only=True, max_digits=10, decimal_places=2)

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


class WithdrawalSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField(read_only=True)

    def get_user_data(self, obj):
        user_data = AdminPublicUserSerializer(
            obj.user, context=self.context).data
        return user_data

    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'amount', 'paypal_email',
                  'status', 'created_at', 'updated_at', 'notes', 'user_data']
        read_only_fields = ['status', 'created_at', 'updated_at']

    def validate(self, data):
        user = data['user']
        amount = data['amount']

        if amount <= 0:
            raise serializers.ValidationError(
                "Amount must be greater than zero")

        if amount > user.user_balance:
            raise serializers.ValidationError(
                "Withdrawal amount cannot exceed available balance")

        return data
