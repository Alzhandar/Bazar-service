from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SalesOrderViewSet,
    InvoiceViewSet,
    SalesOrderListView,
    SalesOrderDetailView,
    SalesOrderCreateView,
    InvoiceListView,
    InvoiceDetailView,
    SalesOrderEditView,
    
)

app_name = 'sales'

router = DefaultRouter()
router.register('orders', SalesOrderViewSet, basename='sales-order')
router.register('invoices', InvoiceViewSet, basename='invoice')

api_urls = [
    path('', include(router.urls)),
]

web_urls = [
    path('orders/', SalesOrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', SalesOrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', SalesOrderCreateView.as_view(), name='order-create'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('orders/<int:pk>/edit/', SalesOrderEditView.as_view(), name='order-edit'),
    path('invoices/<int:pk>/download/', 
         InvoiceDetailView.as_view(template_name='sales/invoice_pdf.html'), 
         name='invoice-pdf'),
]

urlpatterns = web_urls + api_urls