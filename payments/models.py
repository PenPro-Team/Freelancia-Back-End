from django.db import models, transaction
from contract.models import Contract
from decimal import Decimal

class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True)
    method_name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    # api_key_required = models.BooleanField(default=False)
    # api_configuration = models.JSONField(null=True, blank=True)
    client_vat = models.CharField(max_length=50, null=True, blank=True)
    freelancer_vat = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acount_info = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.method_name
    

class Transaction(models.Model):
    STATE_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('compliance_failed', 'Compliance Failed'),
        ('canceled', 'Canceled'),
    )

    id = models.AutoField(primary_key=True)
    contract_client = models.ForeignKey(Contract, null=True, blank=True, on_delete=models.CASCADE, related_name='client_transactions')
    contract_freelancer = models.ForeignKey(Contract, null=True, blank=True, on_delete=models.CASCADE, related_name='freelancer_transactions')
    contract_project = models.ForeignKey(Contract, null=True, blank=True, on_delete=models.CASCADE, related_name='project_transactions')
    contract_budget = models.ForeignKey(Contract, null=True, blank=True, on_delete=models.CASCADE, related_name='budget_transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        'freelancia_back_end.User',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    error_message = models.TextField(null=True, blank=True)

    @property
    def client_vat_amount(self):
        """Calculate VAT amount for client"""
        if self.payment_method.client_vat:
            return (self.amount * Decimal(str(self.payment_method.client_vat))) / Decimal('100')
        return Decimal('0')

    @property
    def freelancer_vat_amount(self):
        """Calculate VAT amount for freelancer"""
        if self.payment_method.freelancer_vat:
            return (self.amount * Decimal(str(self.payment_method.freelancer_vat))) / Decimal('100')
        return Decimal('0')

    @property
    def final_amount(self):
        """Calculate final amount after deducting freelancer VAT"""
        return self.amount - self.freelancer_vat_amount

    @property
    def total_amount_with_vat(self):
        """Calculate total amount including client VAT"""
        return self.amount + self.client_vat_amount

    def save(self, *args, **kwargs):
        """Override save method to ensure data consistency"""
        if not self.pk:  # If this is a new transaction
            with transaction.atomic():
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def process_payment(self):
        """Process the payment with atomic transaction"""
        with transaction.atomic():
            self.state = 'processing'
            self.save()
            
            try:
                # Process payment logic here
                self.state = 'completed'
                self.save()
                return True
            except Exception as e:
                self.state = 'failed'
                self.save()
                raise e

    def get_default_payment_method():
        return PaymentMethod.objects.get_or_create(
            method_name='PayPal',
            defaults={
                'client_vat': 0,
                'freelancer_vat': 0,
                'is_active': True
            }
        )[0].id

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.CASCADE,
        default=get_default_payment_method
    )
    def __str__(self):
        return f"Transaction {self.id} - {self.payment_method.method_name}"


class Withdrawal(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(
        'freelancia_back_end.User',
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paypal_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Withdrawal {self.id} - {self.user.username} - {self.amount}"