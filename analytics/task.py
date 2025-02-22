from celery import shared_task
from datetime import datetime, timedelta
from .service import AnalyticsService
from .models import AnalyticsReport

@shared_task
def generate_daily_reports(user_id):
    date_to = datetime.now().date()
    date_from = date_to - timedelta(days=1)
    
    trading_data = AnalyticsService.get_trading_volume(date_from, date_to)
    AnalyticsReport.objects.create(
        report_type='trading_volume',
        data=list(trading_data),
        created_by_id=user_id,
        date_from=date_from,
        date_to=date_to
    )
    
    sales_data = AnalyticsService.get_sales_performance(date_from, date_to)
    AnalyticsReport.objects.create(
        report_type='sales_performance',
        data=list(sales_data),
        created_by_id=user_id,
        date_from=date_from,
        date_to=date_to
    )

@shared_task
def clean_old_reports():
    thirty_days_ago = datetime.now() - timedelta(days=30)
    AnalyticsReport.objects.filter(created_at__lt=thirty_days_ago).delete()