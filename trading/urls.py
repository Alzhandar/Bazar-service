from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet, 
    TransactionViewSet,
    OrderListView,
    OrderDetailView,
    OrderCreateView,
    TransactionListView
)

app_name = 'trading'

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('transactions', TransactionViewSet, basename='transaction')

api_urls = [
    path('', include(router.urls)),
]

web_urls = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]

urlpatterns = web_urls + api_urls