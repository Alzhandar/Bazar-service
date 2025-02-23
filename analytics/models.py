from django.db import models
from django.contrib.postgres.fields import JSONField
from users.models import User

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