from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'admin'
    TRADER = 'trader'
    SALES = 'sales'
    CUSTOMER = 'customer'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (TRADER, 'Trader'),
        (SALES, 'Sales Representative'),
        (CUSTOMER, 'Customer'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None 
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email