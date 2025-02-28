from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsViewSet,
    AnalyticsReportListView,
    AnalyticsReportDetailView,
    AnalyticsDashboardView,
    ProductPurchaseView,
    StripeWebhookView,
    PaymentSuccessView,
    PaymentHistoryView
)

app_name = 'analytics'

router = DefaultRouter()
router.register('reports', AnalyticsViewSet, basename='report')

api_urls = [
    path('', include(router.urls)),
    path('trading-volume/', 
         AnalyticsViewSet.as_view({'get': 'trading_volume'}),
         name='trading-volume'),
    path('sales-performance/',
         AnalyticsViewSet.as_view({'get': 'sales_performance'}),
         name='sales-performance'),
    path('product-performance/',
         AnalyticsViewSet.as_view({'get': 'product_performance'}),
         name='product-performance'),
    path('generate-reports/',
         AnalyticsViewSet.as_view({'post': 'generate_reports'}),
         name='generate-reports'),
    path('products/<int:pk>/purchase/', 
         ProductPurchaseView.as_view(), 
         name='product-purchase'),
]

urlpatterns = [
    path('dashboard/', 
         AnalyticsDashboardView.as_view(), 
         name='dashboard'),
    path('reports/', 
         AnalyticsReportListView.as_view(), 
         name='report-list'),
    path('reports/<int:pk>/', 
         AnalyticsReportDetailView.as_view(), 
         name='report-detail'),
    
    path('payment/success/', 
         PaymentSuccessView.as_view(), 
         name='payment-success'),
    path('payment/history/', 
         PaymentHistoryView.as_view(), 
         name='payment-history'),
    
    path('webhooks/stripe/', 
         StripeWebhookView.as_view(), 
         name='stripe-webhook'),
    
    path('', include(api_urls)),
]