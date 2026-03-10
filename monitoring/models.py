"""
Monitoring app models – Violations tracking.
"""
from django.db import models


class Violation(models.Model):
    """Records a single monitoring violation during an exam session."""
    VIOLATION_TYPES = (
        ('tab_switch', 'Tab Switch'),
        ('multiple_faces', 'Multiple Faces Detected'),
        ('no_face', 'No Face Detected'),
        ('window_resize', 'Window Resized'),
        ('fullscreen_exit', 'Exited Fullscreen'),
        ('copy_paste', 'Copy/Paste Attempt'),
        ('right_click', 'Right Click Attempt'),
        ('head_movement', 'Suspicious Head Movement'),
        ('identity_mismatch', 'Identity Verification Failure'),
    )

    session = models.ForeignKey(
        'exams.ExamSession',
        on_delete=models.CASCADE,
        related_name='violations',
    )
    violation_type = models.CharField(max_length=30, choices=VIOLATION_TYPES)
    severity_score = models.IntegerField(default=0)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Violation'
        verbose_name_plural = 'Violations'

    def __str__(self):
        return f"[{self.violation_type}] session={self.session_id} score={self.severity_score}"
