from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, PaymentMethodViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]