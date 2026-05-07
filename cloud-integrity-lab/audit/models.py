from django.db import models


class AuditAlert(models.Model):
    SEVERITY_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('CRITICAL', 'Critical'),
    ]
    report = models.ForeignKey(
        'reports.CloudResourceReport', on_delete=models.CASCADE
    )
    detected_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(
        max_length=10, choices=SEVERITY_CHOICES, default='CRITICAL'
    )
    message = models.TextField()
    stored_hash = models.CharField(max_length=64)
    computed_hash = models.CharField(max_length=64)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"[{self.severity}] report={self.report_id} at {self.detected_at:%Y-%m-%d %H:%M:%S}"
