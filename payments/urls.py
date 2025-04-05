from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayPalBalanceChargeView, PayPalCancelView, PayPalSuccessView, TransactionViewSet, PaymentMethodViewSet, create_withdrawal, update_withdrawal_status, get_user_withdrawals

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('paypal/', include([
        path('charge/', PayPalBalanceChargeView.as_view(), name='charge'),
        path('success/', PayPalSuccessView.as_view(), name='success'),
        path('cancel/', PayPalCancelView.as_view(), name='cancel'),
    ])),
    
    # Withdrawal URLs
    path('withdrawals/create/', create_withdrawal, name='create-withdrawal'),
    path('withdrawals/<int:withdrawal_id>/status/', update_withdrawal_status, name='update-withdrawal-status'),
    path('withdrawals/', get_user_withdrawals, name='get-user-withdrawals'),
]