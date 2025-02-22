from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from .models import AnalyticsReport
from .serializers import AnalyticsReportSerializer
from .service import AnalyticsService
from .task import generate_daily_reports


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