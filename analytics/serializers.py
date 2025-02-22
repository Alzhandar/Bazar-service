from rest_framework import serializers
from .models import AnalyticsReport

class AnalyticsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsReport
        fields = ['id', 'report_type', 'data', 'created_by', 
                 'created_at', 'date_from', 'date_to']
        read_only_fields = ['created_by']