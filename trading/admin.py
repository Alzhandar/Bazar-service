from django.contrib import admin
from django.utils.html import format_html
from .models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'order_type', 'quantity', 'price', 'status', 'created_at')
    list_filter = ('status', 'order_type', 'created_at')
    search_fields = ('user__email', 'product__name')
    raw_id_fields = ('user', 'product')
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'product', 'order_type')
        }),
        ('Детали заказа', {
            'fields': ('quantity', 'price', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer_info', 'seller_info', 'quantity', 'price', 'total_amount', 'executed_at')
    list_filter = ('executed_at',)
    search_fields = ('buyer_order__user__email', 'seller_order__user__email')
    raw_id_fields = ('buyer_order', 'seller_order')
    
    def buyer_info(self, obj):
        return f"{obj.buyer_order.user.email} (Buy)"
    buyer_info.short_description = "Покупатель"
    
    def seller_info(self, obj):
        return f"{obj.seller_order.user.email} (Sell)"
    seller_info.short_description = "Продавец"
    
    def total_amount(self, obj):
        return format_html('<b>${:.2f}</b>', obj.price * obj.quantity)
    total_amount.short_description = "Общая сумма"