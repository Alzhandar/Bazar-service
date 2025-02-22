from django.contrib import admin
from django.utils.html import format_html
from .models import SalesOrder, SalesOrderItem, Invoice

class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    raw_id_fields = ('product',)
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'discount', 'total_price')
    readonly_fields = ('total_price',)

    def total_price(self, obj):
        if obj.id:
            return format_html('<b>${:.2f}</b>', obj.total_price)
        return '-'
    total_price.short_description = "Итого"

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_info', 'sales_rep_info', 'total_amount', 
                   'status', 'created_at', 'has_invoice')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__email', 'sales_rep__email', 'notes')
    inlines = [SalesOrderItemInline]
    raw_id_fields = ('customer', 'sales_rep')
    
    fieldsets = (
        ('Участники', {
            'fields': ('customer', 'sales_rep')
        }),
        ('Детали заказа', {
            'fields': ('status', 'notes')
        }),
        ('Финансы', {
            'fields': ('total_amount',),
            'classes': ('collapse',)
        }),
    )
    
    def customer_info(self, obj):
        return f"{obj.customer.email}"
    customer_info.short_description = "Клиент"
    
    def sales_rep_info(self, obj):
        return f"{obj.sales_rep.email}"
    sales_rep_info.short_description = "Менеджер"
    
    def has_invoice(self, obj):
        return hasattr(obj, 'invoice')
    has_invoice.boolean = True
    has_invoice.short_description = "Счет создан"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'sales_order', 'issued_date', 'due_date', 
                   'paid', 'display_pdf')
    list_filter = ('paid', 'issued_date', 'due_date')
    search_fields = ('invoice_number', 'sales_order__customer__email')
    raw_id_fields = ('sales_order',)
    
    def display_pdf(self, obj):
        if obj.pdf_file:
            return format_html('<a href="{}" target="_blank">Открыть PDF</a>', 
                             obj.pdf_file.url)
        return "Нет файла"
    display_pdf.short_description = "PDF файл"