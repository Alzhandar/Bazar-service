from rest_framework import serializers
from .models import SalesOrder, SalesOrderItem, Invoice

class SalesOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 
                 'discount', 'total_price']

class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True)
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    sales_rep_email = serializers.EmailField(source='sales_rep.email', read_only=True)

    class Meta:
        model = SalesOrder
        fields = ['id', 'customer', 'customer_email', 'sales_rep', 
                 'sales_rep_email', 'total_amount', 'status', 'notes', 
                 'items', 'created_at', 'updated_at']
        read_only_fields = ['total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sales_order = SalesOrder.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in items_data:
            item = SalesOrderItem.objects.create(sales_order=sales_order, **item_data)
            total_amount += item.total_price
        
        sales_order.total_amount = total_amount
        sales_order.save()
        return sales_order

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'sales_order', 'invoice_number', 'issued_date', 
                 'due_date', 'paid', 'pdf_file']
        read_only_fields = ['invoice_number']