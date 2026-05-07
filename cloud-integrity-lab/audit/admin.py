from django.contrib import admin
from .models import AuditAlert


@admin.register(AuditAlert)
class AuditAlertAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'severity', 'detected_at', 'resolved')
    list_filter = ('severity', 'resolved')
    search_fields = ('message',)
    readonly_fields = (
        'report', 'detected_at', 'stored_hash', 'computed_hash', 'message'
    )
