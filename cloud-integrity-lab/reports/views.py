from decimal import Decimal

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from audit.models import AuditAlert
from .integrity import compute_report_hash, verify_report_integrity
from .models import CloudResourceReport
from .serializers import (
    CloudResourceReportCreateSerializer,
    CloudResourceReportSerializer,
)


def _flag_tampered(report) -> AuditAlert:
    """Mark report as invalid and create a CRITICAL audit alert."""
    stored = report.report_hash or ''
    computed = compute_report_hash(report)
    if report.is_valid:
        report.is_valid = False
        # Save WITHOUT recomputing the hash. Only is_valid changes.
        report.save(update_fields=['is_valid'])
    alert = AuditAlert.objects.create(
        report=report,
        severity='CRITICAL',
        message=(
            f"Integrity violation detected on report {report.id} "
            f"({report.project_name} {report.month:02d}/{report.year}). "
            f"Stored hash differs from computed hash."
        ),
        stored_hash=stored,
        computed_hash=computed,
    )
    return alert


def _integrity_violation_response(report, alert):
    return Response(
        {
            "error": "INTEGRITY_VIOLATION",
            "message": "Este reporte ha sido alterado. Acceso bloqueado.",
            "report_id": report.id,
            "alert_id": alert.id,
        },
        status=status.HTTP_403_FORBIDDEN,
    )


@api_view(['GET', 'POST'])
def report_list_create(request):
    if request.method == 'POST':
        serializer = CloudResourceReportCreateSerializer(data=request.data)
        serializer.invalid = False
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        services = data['services']
        if 'total_cost' not in data or data.get('total_cost') is None:
            total = sum(Decimal(str(v)) for v in services.values())
            data['total_cost'] = total

        report = CloudResourceReport(
            project_name=data['project_name'],
            month=data['month'],
            year=data['year'],
            services=services,
            total_cost=data['total_cost'],
            currency=data.get('currency', 'USD'),
            is_valid=True,
        )
        report.report_hash = compute_report_hash(report)
        report.save()
        return Response(
            CloudResourceReportSerializer(report).data,
            status=status.HTTP_201_CREATED,
        )

    # GET: list only valid reports (after re-verifying every one)
    reports = CloudResourceReport.objects.all()
    valid = []
    for r in reports:
        if verify_report_integrity(r):
            valid.append(r)
        else:
            _flag_tampered(r)
    return Response(CloudResourceReportSerializer(valid, many=True).data)


@api_view(['GET'])
def report_detail(request, pk):
    report = get_object_or_404(CloudResourceReport, pk=pk)
    if not verify_report_integrity(report):
        alert = _flag_tampered(report)
        return _integrity_violation_response(report, alert)
    return Response(CloudResourceReportSerializer(report).data)


@api_view(['GET'])
def report_verify(request, pk):
    report = get_object_or_404(CloudResourceReport, pk=pk)
    computed = compute_report_hash(report)
    is_intact = (computed == report.report_hash) and bool(report.report_hash)
    payload = {
        "report_id": report.id,
        "project_name": report.project_name,
        "stored_hash": report.report_hash,
        "computed_hash": computed,
        "is_intact": is_intact,
    }
    if not is_intact:
        alert = _flag_tampered(report)
        payload["alert_id"] = alert.id
        payload["message"] = "Integridad comprometida. Alerta generada."
        return Response(payload, status=status.HTTP_403_FORBIDDEN)
    payload["message"] = "Integridad verificada correctamente."
    return Response(payload)


@api_view(['GET'])
def report_stats(request):
    total = CloudResourceReport.objects.count()
    invalid = CloudResourceReport.objects.filter(is_valid=False).count()
    alerts = AuditAlert.objects.count()
    critical_open = AuditAlert.objects.filter(
        severity='CRITICAL', resolved=False
    ).count()
    return Response({
        "total_reports": total,
        "invalid_reports": invalid,
        "valid_reports": total - invalid,
        "total_alerts": alerts,
        "critical_unresolved_alerts": critical_open,
    })
