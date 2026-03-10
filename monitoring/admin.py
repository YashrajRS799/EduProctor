"""Monitoring admin registration."""
from django.contrib import admin
from .models import Violation


@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ['session', 'violation_type', 'severity_score', 'timestamp']
    list_filter = ['violation_type']
    readonly_fields = ['timestamp']
