from django.db import models
from django.contrib.postgres.fields import JSONField
from users.models import User
from django.conf import settings
from products.models import Product

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
    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращено'),
        ('cancelled', 'Отменено'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='payments',
        verbose_name='Пользователь'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='payments',
        verbose_name='Продукт'
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Сумма платежа'
    )
    currency = models.CharField(
        max_length=3, 
        default='USD',
        verbose_name='Валюта'
    )
    payment_intent_id = models.CharField(
        max_length=255, 
        unique=True,
        verbose_name='ID платежа в Stripe'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='Статус платежа'
    )
    checkout_session_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name='ID сессии в Stripe'
    )
    payment_method = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Метод оплаты'
    )
    billing_details = models.JSONField(
        blank=True, 
        null=True,
        verbose_name='Детали оплаты'
    )
    error_message = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Сообщение об ошибке'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    completed_at = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name='Дата завершения'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_intent_id']),
            models.Index(fields=['status']),
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Платеж {self.payment_intent_id} - {self.get_status_display()}"

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_pending(self):
        return self.status == 'pending'

    @property
    def is_failed(self):
        return self.status == 'failed'


