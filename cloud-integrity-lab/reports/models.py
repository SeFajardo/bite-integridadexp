from django.db import models


class CloudResourceReport(models.Model):
    project_name = models.CharField(max_length=100)
    month = models.IntegerField()
    year = models.IntegerField()
    services = models.JSONField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    consolidated_at = models.DateTimeField(auto_now_add=True)
    report_hash = models.CharField(max_length=64, blank=True)
    is_valid = models.BooleanField(default=True)

    class Meta:
        unique_together = ('project_name', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.project_name} {self.month:02d}/{self.year}"
