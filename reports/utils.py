"""
Reports app utility – generate IntegrityReport from a finished ExamSession.
"""
from .models import IntegrityReport
from monitoring.scoring import calculate_risk_level, calculate_integrity_score
from monitoring.models import Violation


def generate_integrity_report(session):
    """
    Build or update an IntegrityReport for the given ExamSession.
    Called automatically when a student submits an exam.
    """
    violations = Violation.objects.filter(session=session)
    total_violations = violations.count()
    total_score = session.total_violation_score
    risk_level = calculate_risk_level(total_score)
    final_score = calculate_integrity_score(total_score)

    # Build a notes summary
    from django.db.models import Count
    breakdown = violations.values('violation_type').annotate(count=Count('id'))
    notes_lines = [f"{v['violation_type'].replace('_', ' ').title()}: {v['count']}x" for v in breakdown]
    notes = '\n'.join(notes_lines) if notes_lines else 'No violations recorded.'

    report, _ = IntegrityReport.objects.update_or_create(
        session=session,
        defaults={
            'total_violations': total_violations,
            'total_violation_score': total_score,
            'final_score': final_score,
            'risk_level': risk_level,
            'notes': notes,
        },
    )
    return report
