from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from django.views import View

from users.permissions import IsAdmin
from products.models import Product
from .models import AnalyticsReport, Payment
from .serializers import AnalyticsReportSerializer
from .service import AnalyticsService, PaymentService

import json
import logging
import stripe

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsReport.objects.all()
    serializer_class = AnalyticsReportSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def trading_volume(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = AnalyticsService.get_trading_volume(date_from, date_to)
        return Response(data)

    @action(detail=False, methods=['get'])
    def sales_performance(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = AnalyticsService.get_sales_performance(date_from, date_to)
        return Response(data)

    @action(detail=False, methods=['get'])
    def product_performance(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        data = AnalyticsService.get_product_performance(date_from, date_to)
        
        return Response(data)
    
    @action(detail=False, methods=['post'])
    def generate_reports(self, request):
        task = generate_daily_reports.delay(request.user.id)
        return Response({
            'task_id': task.id,
            'status': 'Reports generation started'
        })
    
class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'analyst']
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        context.update(AnalyticsService.get_dashboard_data(date_from, date_to))
        
        return context

class AnalyticsReportListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AnalyticsReport
    template_name = 'analytics/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.role in ['admin', 'analyst']

class AnalyticsReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AnalyticsReport
    template_name = 'analytics/report_detail.html'
    context_object_name = 'report'
    
    def test_func(self):
        return self.request.user.role in ['admin', 'analyst']
    

@method_decorator(csrf_exempt, name='dispatch')
class ProductPurchaseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            product = get_object_or_404(Product, pk=pk)
            
            if product.stock <= 0:
                return JsonResponse({
                    'error': 'Товар временно недоступен'
                }, status=400)

            payment_intent = PaymentService.create_payment_intent(product, request.user)

            payment = Payment.objects.create(
                user=request.user,
                product=product,
                amount=product.price,
                stripe_payment_intent_id=payment_intent.id
            )

            return JsonResponse({
                'clientSecret': payment_intent.client_secret,
                'payment_id': payment.id
            })

        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Произошла ошибка при обработке платежа'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Webhook-обработчик для событий Stripe
    """
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        if not sig_header:
            logger.error("Missing Stripe signature header")
            return Response({'error': 'Missing signature header'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Обрабатываем webhook через сервисный класс
            result = PaymentService.handle_payment_webhook(payload, sig_header)
            
            if result.get('status') == 'error':
                logger.error(f"Ошибка обработки webhook: {result.get('message')}")
                return Response({'error': result.get('message')}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/payment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        product_id = self.request.GET.get('product_id')
        payment_intent_id = self.request.GET.get('payment_intent')
        
        if product_id:
            context['product'] = get_object_or_404(Product, pk=product_id)
        
        if payment_intent_id:
            try:
                payment = Payment.objects.get(payment_intent_id=payment_intent_id)
                context['payment'] = payment
                context['product'] = payment.product
            except Payment.DoesNotExist:
                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    if payment_intent and payment_intent.status == 'succeeded':
                        context['payment_status'] = 'completed'
                        product_id = payment_intent.metadata.get('product_id')
                        if product_id:
                            context['product'] = get_object_or_404(Product, pk=product_id)
                except Exception as e:
                    logger.error(f"Ошибка при получении данных из Stripe: {str(e)}")
                    context['payment_status'] = 'unknown'
        
        return context


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """
    История платежей пользователя
    """
    template_name = 'analytics/payment_history.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')