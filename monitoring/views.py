"""
Monitoring app views – AJAX violation logging endpoint.
"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from exams.models import ExamSession
from .models import Violation
from .scoring import get_severity


@login_required
@require_POST
def log_violation(request):
    """
    AJAX endpoint: receive a violation event from the browser monitoring JS.
    Expected POST body (JSON):
        { "session_id": 5, "violation_type": "tab_switch", "details": "" }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    session_id = data.get('session_id')
    violation_type = data.get('violation_type', '')
    details = data.get('details', '')

    # Validate session ownership
    try:
        session = ExamSession.objects.get(id=session_id, student=request.user, status='in_progress')
    except ExamSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

    severity = get_severity(violation_type)

    # Create violation record
    Violation.objects.create(
        session=session,
        violation_type=violation_type,
        severity_score=severity,
        details=details,
    )

    # Update cumulative violation score on session
    session.total_violation_score += severity
    # Auto-flag sessions with extreme violations
    if session.total_violation_score > 80:
        session.status = 'flagged'
    session.save(update_fields=['total_violation_score', 'status'])

    return JsonResponse({
        'status': 'ok',
        'severity': severity,
        'total_score': session.total_violation_score,
    })


@login_required
@require_POST
def webcam_status(request):
    """
    AJAX endpoint: receive webcam analysis results from OpenCV subprocess.
    Expected POST body (JSON):
        { "session_id": 5, "face_count": 0, "details": "No face detected" }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    session_id = data.get('session_id')
    face_count = data.get('face_count', -1)
    details = data.get('details', '')

    try:
        session = ExamSession.objects.get(id=session_id, student=request.user, status='in_progress')
    except ExamSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

    # Determine violation type from face count or explicit type
    violation_type = data.get('violation_type')
    
    if not violation_type:
        if face_count == 0:
            violation_type = 'no_face'
        elif face_count > 1:
            violation_type = 'multiple_faces'
        else:
            # Normal – single face detected, no violation
            return JsonResponse({'status': 'ok', 'violation': None})

    severity = get_severity(violation_type)
    Violation.objects.create(
        session=session,
        violation_type=violation_type,
        severity_score=severity,
        details=details,
    )
    session.total_violation_score += severity
    session.save(update_fields=['total_violation_score'])

    return JsonResponse({'status': 'ok', 'violation': violation_type, 'severity': severity})
