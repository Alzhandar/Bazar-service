from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Order, Transaction
from .serializers import OrderSerializer, TransactionSerializer
from products.models import Product

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'order_type']
    ordering_fields = ['created_at', 'price']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'order cancelled'})
        return Response({'error': 'can only cancel pending orders'}, 
                      status=status.HTTP_400_BAD_REQUEST)

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['executed_at', 'price']

    def get_queryset(self):
        user_orders = Order.objects.filter(user=self.request.user)
        return Transaction.objects.filter(
            buyer_order__in=user_orders
        ) | Transaction.objects.filter(
            seller_order__in=user_orders
        )

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'trading/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        status_filter = self.request.GET.get('status', '')
        type_filter = self.request.GET.get('type', '')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if type_filter:
            queryset = queryset.filter(order_type=type_filter)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['type_filter'] = self.request.GET.get('type', '')
        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = 'trading/order_form.html'
    fields = ['product', 'order_type', 'quantity', 'price']
    success_url = reverse_lazy('order-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'trading/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'trading/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        user_orders = Order.objects.filter(user=self.request.user)
        return Transaction.objects.filter(
            Q(buyer_order__in=user_orders) |
            Q(seller_order__in=user_orders)
        ).order_by('-executed_at')