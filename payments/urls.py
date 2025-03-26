from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayPalBalanceChargeView, PayPalCancelView, PayPalSuccessView, TransactionViewSet, PaymentMethodViewSet

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
]