"""Reports admin registration."""
from django.contrib import admin
from .models import IntegrityReport


@admin.register(IntegrityReport)
class IntegrityReportAdmin(admin.ModelAdmin):
    list_display = ['session', 'total_violations', 'final_score', 'risk_level', 'generated_at']
    list_filter = ['risk_level']
    readonly_fields = ['generated_at']
