from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from products.models import Product

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    ORDER_TYPE = (
        ('buy', 'Buy'),
        ('sell', 'Sell')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=4, choices=ORDER_TYPE)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_type} - {self.product.name} ({self.quantity})"

class Transaction(models.Model):
    buyer_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='buy_transactions')
    seller_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='sell_transactions')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-executed_at']

    def __str__(self):
        return f"Transaction: {self.quantity} @ {self.price}"