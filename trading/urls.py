from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, TransactionViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]