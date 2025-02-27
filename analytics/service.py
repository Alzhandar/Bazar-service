from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from sales.models import SalesOrder, SalesOrderItem
from products.models import Product
from users.models import User

class AnalyticsService:
    @staticmethod
    def get_date_range(date_from=None, date_to=None):
        """
        Возвращает диапазон дат для аналитики.
        Принимает строки в формате YYYY-MM-DD или объекты datetime.
        Если даты не указаны, возвращает последние 30 дней.
        """
        try:
            # Обработка начальной даты
            if date_from:
                if isinstance(date_from, str):
                    date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d')
                date_from = timezone.make_aware(
                    date_from.replace(hour=0, minute=0, second=0, microsecond=0)
                ) if timezone.is_naive(date_from) else date_from
            else:
                date_from = timezone.now() - timedelta(days=30)

            # Обработка конечной даты
            if date_to:
                if isinstance(date_to, str):
                    date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d')
                date_to = timezone.make_aware(
                    date_to.replace(hour=23, minute=59, second=59, microsecond=999999)
                ) if timezone.is_naive(date_to) else date_to
            else:
                date_to = timezone.now()

            # Убедимся, что date_from меньше date_to
            if date_from > date_to:
                date_from, date_to = date_to, date_from

        except (ValueError, TypeError):
            # В случае ошибки парсинга дат, используем последние 30 дней
            date_to = timezone.now()
            date_from = date_to - timedelta(days=30)

        return date_from, date_to

    @staticmethod
    def get_trading_volume(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        volume = SalesOrderItem.objects.filter(
            sales_order__created_at__range=(date_from, date_to),  
            sales_order__status='completed'
        ).aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=DecimalField())
        )['total'] or Decimal('0')
        
        return volume

    @staticmethod
    def get_sales_performance(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return SalesOrder.objects.filter(
            created_at__range=(date_from, date_to)
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            orders_count=Count('id'),
            total_amount=Sum(
                F('items__quantity') * F('items__unit_price'),
                output_field=DecimalField()
            )
        ).order_by('date')

    @staticmethod
    def get_product_performance(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return Product.objects.filter(
            salesorderitem__sales_order__created_at__range=(date_from, date_to),  # Изменено
            salesorderitem__sales_order__status='completed'
        ).annotate(
            sales_count=Count('salesorderitem'),  # Изменено
            revenue=Sum(
                F('salesorderitem__quantity') * F('salesorderitem__unit_price'),  # Изменено
                output_field=DecimalField()
            ),
            avg_price=Avg('salesorderitem__unit_price')  # Изменено
        ).order_by('-revenue')[:10]

    @staticmethod
    def get_top_sellers(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return User.objects.filter(
            sales_orders__created_at__range=(date_from, date_to),  # Изменено с orders на sales_orders
            sales_orders__status='completed'
        ).annotate(
            total_sales=Sum(
                F('sales_orders__items__quantity') * F('sales_orders__items__unit_price'),  # Изменено
                output_field=DecimalField()
            ),
            orders_count=Count('sales_orders', distinct=True),  # Изменено
            conversion=ExpressionWrapper(
                (Count('sales_orders', filter=F('sales_orders__status')=='completed', distinct=True) * 100.0) /  # Изменено
                Count('sales_orders', distinct=True),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('-total_sales')[:5]

    @staticmethod
    def get_dashboard_data(date_from=None, date_to=None):
        date_from, date_to = AnalyticsService.get_date_range(date_from, date_to)
        
        return {
            'trading_volume': AnalyticsService.get_trading_volume(date_from, date_to),
            'orders_count': SalesOrder.objects.filter(
                created_at__range=(date_from, date_to),
                status='completed'
            ).count(),
            'active_users': User.objects.filter(
                sales_orders__created_at__range=(date_from, date_to)  # Изменено
            ).distinct().count(),
            'conversion_rate': SalesOrder.objects.filter(
                created_at__range=(date_from, date_to)
            ).aggregate(
                conversion=ExpressionWrapper(
                    (Count('id', filter=F('status')=='completed') * 100.0) /
                    Count('id'),
                    output_field=DecimalField(max_digits=5, decimal_places=2)
                )
            )['conversion'] or Decimal('0'),
            'sales_performance': AnalyticsService.get_sales_performance(date_from, date_to),
            'top_products': AnalyticsService.get_product_performance(date_from, date_to),
            'top_sellers': AnalyticsService.get_top_sellers(date_from, date_to)
        }