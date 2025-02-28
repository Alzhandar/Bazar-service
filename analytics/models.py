from django.db import models
from django.contrib.postgres.fields import JSONField
from users.models import User
from django.conf import settings


class AnalyticsReport(models.Model):
    REPORT_TYPES = (
        ('trading_volume', 'Trading Volume'),
        ('sales_performance', 'Sales Performance'),
        ('revenue_analysis', 'Revenue Analysis'),
        ('product_performance', 'Product Performance'),
    )

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    data = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    date_from = models.DateField()
    date_to = models.DateField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report_type} Report ({self.date_from} - {self.date_to})"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
        ('refunded', 'Возвращен'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.status})"