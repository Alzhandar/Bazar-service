from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from .models import AnalyticsReport
from .serializers import AnalyticsReportSerializer
from .service import AnalyticsService
from .task import generate_daily_reports
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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