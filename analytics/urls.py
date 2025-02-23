from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsViewSet,
    AnalyticsReportListView,
    AnalyticsReportDetailView,
    AnalyticsDashboardView
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
]

web_urls = [
    path('', AnalyticsDashboardView.as_view(), name='dashboard'),
    path('reports/', AnalyticsReportListView.as_view(), name='report-list'),
    path('reports/<int:pk>/', AnalyticsReportDetailView.as_view(), name='report-detail'),
]

urlpatterns = web_urls + api_urls