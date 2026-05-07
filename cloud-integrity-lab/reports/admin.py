from django.contrib import admin
from .models import CloudResourceReport


@admin.register(CloudResourceReport)
class CloudResourceReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'project_name', 'month', 'year',
        'total_cost', 'currency', 'is_valid', 'consolidated_at',
    )
    list_filter = ('is_valid', 'project_name', 'year')
    search_fields = ('project_name',)
    readonly_fields = ('report_hash', 'consolidated_at')
