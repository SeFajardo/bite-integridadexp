from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import AuditAlert
from .serializers import AuditAlertSerializer


@api_view(['GET'])
def alert_list(request):
    alerts = AuditAlert.objects.all()
    return Response(AuditAlertSerializer(alerts, many=True).data)


@api_view(['GET'])
def alert_detail(request, pk):
    alert = get_object_or_404(AuditAlert, pk=pk)
    return Response(AuditAlertSerializer(alert).data)


@api_view(['PATCH'])
def alert_resolve(request, pk):
    alert = get_object_or_404(AuditAlert, pk=pk)
    alert.resolved = True
    alert.save(update_fields=['resolved'])
    return Response(AuditAlertSerializer(alert).data, status=status.HTTP_200_OK)


@api_view(['GET'])
def audit_dashboard(request):
    total = AuditAlert.objects.count()
    critical_open = AuditAlert.objects.filter(
        severity='CRITICAL', resolved=False
    ).count()
    latest = AuditAlert.objects.all()[:5]
    return Response({
        "total_alerts": total,
        "critical_unresolved": critical_open,
        "latest_alerts": AuditAlertSerializer(latest, many=True).data,
    })
