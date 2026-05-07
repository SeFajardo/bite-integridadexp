from rest_framework import serializers
from .models import AuditAlert


class AuditAlertSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(
        source='report.project_name', read_only=True
    )

    class Meta:
        model = AuditAlert
        fields = [
            'id', 'report', 'project_name', 'detected_at',
            'severity', 'message', 'stored_hash', 'computed_hash',
            'resolved',
        ]
        read_only_fields = fields
