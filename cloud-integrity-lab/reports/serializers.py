from rest_framework import serializers
from .models import CloudResourceReport


class CloudResourceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudResourceReport
        fields = [
            'id', 'project_name', 'month', 'year', 'services',
            'total_cost', 'currency', 'consolidated_at',
            'report_hash', 'is_valid',
        ]
        read_only_fields = ['id', 'consolidated_at', 'report_hash', 'is_valid']


class CloudResourceReportCreateSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )

    class Meta:
        model = CloudResourceReport
        fields = ['project_name', 'month', 'year', 'services', 'total_cost', 'currency']

    def validate_services(self, value):
        if not isinstance(value, dict) or not value:
            raise serializers.ValidationError("services must be a non-empty object")
        for k, v in value.items():
            if not isinstance(v, (int, float)):
                raise serializers.ValidationError(f"service '{k}' cost must be numeric")
        return value

    def validate_month(self, value):
        if not 1 <= value <= 12:
            raise serializers.ValidationError("month must be in 1..12")
        return value
