from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO

from .models import SalesOrder, SalesOrderItem, Invoice
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

class SalesOrderListView(LoginRequiredMixin, ListView):
    model = SalesOrder
    template_name = 'sales/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return SalesOrder.objects.all()
        elif user.role == 'sales':
            return SalesOrder.objects.filter(sales_rep=user)
        return SalesOrder.objects.filter(customer=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        return context

class SalesOrderDetailView(LoginRequiredMixin, DetailView):
    model = SalesOrder
    template_name = 'sales/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

class SalesOrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SalesOrder
    template_name = 'sales/order_form.html'
    fields = ['customer', 'notes']
    success_url = reverse_lazy('sales-order-list')

    def test_func(self):
        return self.request.user.role in ['admin', 'sales']

    def form_valid(self, form):
        form.instance.sales_rep = self.request.user
        return super().form_valid(form)

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'sales/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Invoice.objects.all()
        elif user.role == 'sales':
            return Invoice.objects.filter(sales_order__sales_rep=user)
        return Invoice.objects.filter(sales_order__customer=user)
    
def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(template.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'sales/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.object.sales_order
        context['items'] = self.object.sales_order.items.all()
        return context

    def get(self, request, *args, **kwargs):
        if 'download' in request.GET:
            invoice = self.get_object()
            context = {
                'invoice': invoice,
                'order': invoice.sales_order,
                'items': invoice.sales_order.items.all(),
                'company_name': 'Your Company Name',
                'company_address': 'Your Company Address',
            }
            pdf = render_to_pdf('sales/invoice_pdf.html', context)
            if pdf:
                response = pdf
                filename = f"invoice_{invoice.invoice_number}.pdf"
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            return HttpResponse("Error generating PDF", status=500)
        return super().get(request, *args, **kwargs)