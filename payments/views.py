from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from contract.models import Contract
from .models import Transaction, PaymentMethod
from .serializers import TransactionSerializer, PaymentMethodSerializer

import logging
logger = logging.getLogger(__name__)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                logger.info(f"Attempting to create transaction with data: {request.data}")
                
                # Validate payment method exists
                try:
                    payment_method = PaymentMethod.objects.get(id=request.data.get('payment_method'))
                except PaymentMethod.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Payment method does not exist'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validate contract exists
                try:
                    contract = Contract.objects.get(id=request.data.get('contract_client'))
                except Contract.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Contract does not exist'
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error creating transaction: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': str(e),
                    'data': request.data
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        with transaction.atomic():
            try:
                transaction_obj = self.get_object()
                
                # 1. تحديث حالة المعاملة إلى processing
                transaction_obj.state = 'processing'
                transaction_obj.save()

                # 2. خصم المبلغ من العميل (هنا يمكن إضافة المنطق الخاص بك)
                client_amount = transaction_obj.amount + transaction_obj.client_vat_amount
                # update_client_balance(transaction_obj.contract_client, -client_amount)

                # 3. إضافة المبلغ للمستقل
                freelancer_amount = transaction_obj.final_amount
                # update_freelancer_balance(transaction_obj.contract_freelancer, freelancer_amount)

                # 4. تحديث حالة المعاملة إلى completed
                transaction_obj.state = 'completed'
                transaction_obj.save()

                return Response({
                    'status': 'success',
                    'message': 'Payment processed successfully',
                    'total_amount': transaction_obj.total_amount_with_vat,
                    'vat_amount': transaction_obj.client_vat_amount,
                    'freelancer_receives': transaction_obj.final_amount
                })

            except Exception as e:
                # في حالة حدوث أي خطأ، سيتم التراجع عن كل التغييرات تلقائياً
                transaction_obj.state = 'failed'
                transaction_obj.save()
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def contracts_info(self, request):
        """Get all contracts info for testing"""
        contracts = Contract.objects.all()
        contracts_data = []
        
        for contract in contracts:
            contracts_data.append({
                'id': contract.id,
                'client': {
                    'id': contract.client.id,
                    'username': contract.client.username
                },
                'freelancer': {
                    'id': contract.freelancer.id,
                    'username': contract.freelancer.username
                },
                'project': {
                    'id': contract.project.id,
                    'name': str(contract.project)
                },
                'budget': contract.budget,
                'state': contract.contract_state
            })
        
        return Response({
            'message': 'Available contracts for testing',
            'contracts': contracts_data
        })