"""
Reports app models – IntegrityReport.
"""
from django.db import models
from django.utils import timezone


class IntegrityReport(models.Model):
    """Auto-generated report summarizing exam session integrity."""
    RISK_LEVELS = (
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    )

    session = models.OneToOneField(
        'exams.ExamSession',
        on_delete=models.CASCADE,
        related_name='integrity_report',
    )
    total_violations = models.IntegerField(default=0)
    total_violation_score = models.IntegerField(default=0)
    final_score = models.FloatField(default=100.0)   # 0–100 integrity score
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='low')
    generated_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Integrity Report'
        verbose_name_plural = 'Integrity Reports'

    def __str__(self):
        return (
            f"Report – {self.session.student.username} | "
            f"{self.session.exam.title} | Risk: {self.risk_level.upper()}"
        )
