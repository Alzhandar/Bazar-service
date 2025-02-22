from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import SalesOrder, Invoice
from .serializers import SalesOrderSerializer, InvoiceSerializer
from users.permissions import IsSales, IsAdmin

class SalesOrderViewSet(viewsets.ModelViewSet):
    serializer_class = SalesOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return SalesOrder.objects.all()
        elif user.role == 'sales':
            return SalesOrder.objects.filter(sales_rep=user)
        return SalesOrder.objects.filter(customer=user)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsSales()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'approved'
            order.save()
            return Response({'status': 'order approved'})
        return Response(
            {'error': 'can only approve pending orders'},
            status=status.HTTP_400_BAD_REQUEST
        )

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAdmin]