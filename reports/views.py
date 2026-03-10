"""
Reports app views – View, list, and export integrity reports.
"""
import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

from exams.models import ExamSession, Exam
from monitoring.models import Violation
from .models import IntegrityReport


@login_required
def report_detail(request, session_id):
    """Show detailed integrity report for a session."""
    session = get_object_or_404(ExamSession, id=session_id)

    # Students can only see their own reports
    if request.user.is_student_user and session.student != request.user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:student_dashboard')

    try:
        report = session.integrity_report
    except IntegrityReport.DoesNotExist:
        # Generate on-demand if missing
        from .utils import generate_integrity_report
        report = generate_integrity_report(session)

    violations = Violation.objects.filter(session=session).order_by('-timestamp')
    answers = session.answers.select_related('question').all()

    context = {
        'session': session,
        'report': report,
        'violations': violations,
        'answers': answers,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_list(request):
    """Admin: list all integrity reports, filterable by exam."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    exams = Exam.objects.filter(created_by=request.user)
    selected_exam_id = request.GET.get('exam')

    sessions = ExamSession.objects.filter(
        exam__created_by=request.user
    ).select_related('student', 'exam', 'integrity_report').order_by('-start_time')

    if selected_exam_id:
        sessions = sessions.filter(exam_id=selected_exam_id)

    context = {
        'sessions': sessions,
        'exams': exams,
        'selected_exam_id': int(selected_exam_id) if selected_exam_id else None,
    }
    return render(request, 'reports/report_list.html', context)


@login_required
def export_report_csv(request):
    """Admin: export integrity reports as CSV."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="eduproctor_reports.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Student', 'Exam', 'Start Time', 'End Time', 'Status',
        'Score', 'Total Marks', 'Percentage',
        'Total Violations', 'Violation Score', 'Integrity Score', 'Risk Level',
    ])

    sessions = ExamSession.objects.filter(
        exam__created_by=request.user
    ).select_related('student', 'exam').order_by('-start_time')

    for session in sessions:
        try:
            report = session.integrity_report
            int_score = report.final_score
            risk = report.risk_level
            tot_viol = report.total_violations
        except IntegrityReport.DoesNotExist:
            int_score = 'N/A'
            risk = 'N/A'
            tot_viol = 'N/A'

        writer.writerow([
            session.student.username,
            session.exam.title,
            session.start_time.strftime('%Y-%m-%d %H:%M'),
            session.end_time.strftime('%Y-%m-%d %H:%M') if session.end_time else 'In Progress',
            session.get_status_display(),
            session.score,
            session.total_marks,
            session.percentage,
            tot_viol,
            session.total_violation_score,
            int_score,
            risk,
        ])

    return response
