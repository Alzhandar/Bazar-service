from rest_framework import serializers
from .models import Order, Transaction

class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_email', 'product', 'product_name', 
                 'order_type', 'quantity', 'price', 'status', 'total_amount',
                 'created_at', 'updated_at']
        read_only_fields = ['status', 'user']

    def validate(self, data):
        if data['order_type'] == 'buy' and data['product'].stock < data['quantity']:
            raise serializers.ValidationError("Not enough stock available")
        return data

class TransactionSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer_order.user.email', read_only=True)
    seller_email = serializers.EmailField(source='seller_order.user.email', read_only=True)
    product_name = serializers.CharField(source='buyer_order.product.name', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'buyer_order', 'buyer_email', 'seller_order', 
                 'seller_email', 'product_name', 'quantity', 'price', 
                 'executed_at']