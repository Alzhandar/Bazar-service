from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from trading.models import Transaction
from sales.models import SalesOrder
from products.models import Product

class AnalyticsService:
    @staticmethod
    def get_trading_volume(date_from, date_to):
        return Transaction.objects.filter(
            executed_at__date__range=[date_from, date_to]
        ).annotate(
            date=TruncDate('executed_at')
        ).values('date').annotate(
            volume=Sum('quantity'),
            total_value=Sum('price')
        ).order_by('date')

    @staticmethod
    def get_sales_performance(date_from, date_to):
        return SalesOrder.objects.filter(
            created_at__date__range=[date_from, date_to]
        ).annotate(
            date=TruncDate('created_at')
        ).values('date', 'sales_rep__email').annotate(
            orders_count=Count('id'),
            total_sales=Sum('total_amount')
        ).order_by('date')

    @staticmethod
    def get_product_performance(date_from, date_to):
        return Product.objects.filter(
            orders__created_at__date__range=[date_from, date_to]
        ).annotate(
            total_orders=Count('orders'),
            total_revenue=Sum('orders__total_amount')
        ).order_by('-total_revenue')