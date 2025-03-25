from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from django.db import transaction
from contract.models import Contract
from freelancia import settings
from .models import Transaction, PaymentMethod
from .serializers import TransactionSerializer, PaymentMethodSerializer
import paypalrestsdk
from decimal import Decimal
from rest_framework.views import APIView
import logging
logger = logging.getLogger(__name__)

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET
})

from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
User = get_user_model()

class PayPalBalanceChargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Initiating PayPal payment for user {request.user.username}")
        amount = request.data.get('amount')
        if not amount:
            return Response({
                'status': 'error',
                'message': 'Amount is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1] if auth_header and auth_header.startswith('Bearer ') else None
        
        if not token:
            return Response({
                'status': 'error',
                'message': 'Bearer token not found'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Create PayPal payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{request.build_absolute_uri(reverse('success'))}?user_id={request.user.id}",
                "cancel_url": request.build_absolute_uri(reverse('cancel'))
            },
            "transactions": [{
                "amount": {
                    "total": str(amount),
                    "currency": "USD"
                },
                "description": f"Balance charge for {request.user.username}"
            }]
        })

        if payment.create():
            logger.info(f"PayPal payment created successfully: {payment.id}")
            redirect_url = next(link.href for link in payment.links if link.method == "REDIRECT")
            return Response({
                'status': 'success',
                'redirect_url': redirect_url,
                'payment_id': payment.id
            })
        else:
            logger.error(f"PayPal payment creation failed: {payment.error}")
            return Response({
                'status': 'error',
                'message': 'Failed to create PayPal payment'
            }, status=status.HTTP_400_BAD_REQUEST)

class PayPalSuccessView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        user_id = request.GET.get('user_id')
        
        if not all([payment_id, payer_id, user_id]):
            return Response({
                'status': 'error',
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.select_for_update().get(id=user_id)
            
            try:
                # Find the payment first
                payment = paypalrestsdk.Payment.find(payment_id)
                if not payment:
                    raise ValueError("Payment not found")
                payment_execution = payment.execute({"payer_id": payer_id})
                print(payment_execution)
                # Execute the payment correctly
                if payment_execution:
                    logger.info(f"PayPal payment executed successfully for payment {payment_id}")
                    amount = Decimal(payment.transactions[0].amount.total)
                    
                    with transaction.atomic():
                        # Update user balance
                        user.user_balance += amount
                        user.save()
                        
                        logger.info(f"Balance updated successfully for user {user.username}")
                        return Response({
                            'status': 'success',
                            'message': 'Payment successful and balance updated',
                            'new_balance': user.user_balance
                        })
                else:
                    error_msg = payment.error.get('message', 'Payment execution failed')
                    logger.error(f"PayPal execution failed: {error_msg}")
                    return Response({
                        'status': 'error',
                        'message': error_msg
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except paypalrestsdk.exceptions.ResourceNotFound:
                logger.error(f"Payment {payment_id} not found")
                return Response({
                    'status': 'error',
                    'message': 'Payment not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Payment execution error: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Payment verification error: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PayPalCancelView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            'status': 'cancelled',
            'message': 'Payment was cancelled'
        })

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