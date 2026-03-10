"""
Exams app views – Exam CRUD, session management, grading.
"""
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Exam, Question, ExamSession, StudentAnswer
from .forms import ExamForm, QuestionForm, QuestionFormSet
from reports.utils import generate_integrity_report


# ─────────────────────────── ADMIN VIEWS ───────────────────────────

@login_required
def exam_list(request):
    """Admin: list all exams they created."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')
    exams = Exam.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'exams/exam_list.html', {'exams': exams})


@login_required
def create_exam(request):
    """Admin: create a new exam."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    form = ExamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exam = form.save(commit=False)
        exam.created_by = request.user
        exam.save()
        messages.success(request, f'Exam "{exam.title}" created. Now add questions.')
        return redirect('exams:add_questions', exam_id=exam.id)

    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def add_questions(request, exam_id):
    """Admin: add/edit questions for a specific exam."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    existing_qs = Question.objects.filter(exam=exam)

    if request.method == 'POST':
        formset = QuestionFormSet(request.POST, queryset=existing_qs)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for idx, instance in enumerate(instances):
                instance.exam = exam
                instance.order = idx + 1
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, f'{len(instances)} question(s) saved.')
            return redirect('exams:exam_detail', exam_id=exam.id)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        formset = QuestionFormSet(queryset=existing_qs)

    return render(request, 'exams/add_questions.html', {'exam': exam, 'formset': formset})


@login_required
def exam_detail(request, exam_id):
    """Admin: view details and statistics for an exam."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    sessions = ExamSession.objects.filter(exam=exam).select_related('student').order_by('-start_time')

    return render(request, 'exams/exam_detail.html', {
        'exam': exam,
        'questions': questions,
        'sessions': sessions,
    })


@login_required
def edit_exam(request, exam_id):
    """Admin: edit exam details (date/time, title, etc.)."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    form = ExamForm(request.POST or None, instance=exam)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Exam "{exam.title}" updated.')
        return redirect('exams:exam_detail', exam_id=exam.id)

    return render(request, 'exams/create_exam.html', {'form': form, 'is_edit': True, 'exam': exam})


@login_required
@require_POST
def delete_exam(request, exam_id):
    """Admin: delete an exam."""
    if not request.user.is_admin_user:
        return redirect('accounts:student_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    title = exam.title
    exam.delete()
    messages.success(request, f'Exam "{title}" has been deleted.')
    return redirect('exams:exam_list')


# ─────────────────────────── STUDENT VIEWS ───────────────────────────

@login_required
def student_exam_list(request):
    """Student: list available exams."""
    if not request.user.is_student_user:
        return redirect('accounts:admin_dashboard')

    now = timezone.now()
    available = Exam.objects.filter(is_active=True, start_time__lte=now, end_time__gte=now)
    attempted_ids = ExamSession.objects.filter(
        student=request.user
    ).values_list('exam_id', flat=True)

    return render(request, 'exams/student_exam_list.html', {
        'available_exams': available,
        'attempted_ids': list(attempted_ids),
    })


@login_required
def start_exam(request, exam_id):
    """Student: start an exam session."""
    if not request.user.is_student_user:
        return redirect('accounts:admin_dashboard')

    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    now = timezone.now()

    # Validate availability window
    if not (exam.start_time <= now <= exam.end_time):
        messages.error(request, 'This exam is not currently available.')
        return redirect('accounts:student_dashboard')

    # Check for existing session
    session, created = ExamSession.objects.get_or_create(
        student=request.user,
        exam=exam,
        defaults={'status': 'in_progress', 'total_marks': exam.question_count},
    )

    if not created and session.status in ('completed', 'flagged', 'timed_out'):
        messages.warning(request, 'You have already completed this exam.')
        return redirect('accounts:student_dashboard')

    # Identity Verification Check
    if not session.id_verified:
        return redirect('exams:verify_identity', session_id=session.id)

    questions = exam.questions.all().order_by('order')

    # Calculate remaining time in seconds
    elapsed = int((now - session.start_time).total_seconds())
    remaining = max(0, exam.duration_minutes * 60 - elapsed)

    return render(request, 'exams/exam_interface.html', {
        'exam': exam,
        'session': session,
        'questions': questions,
        'remaining_seconds': remaining,
    })


@login_required
def verify_identity(request, session_id):
    """Student: take a photo to verify identity before starting exam."""
    session = get_object_or_404(ExamSession, id=session_id, student=request.user)
    
    if session.id_verified:
        return redirect('exams:start_exam', exam_id=session.exam.id)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            if image_data:
                # Process base64 image
                import base64
                from django.core.files.base import ContentFile
                
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = f"verify_{session.id}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=file_name)
                
                session.verification_image = data
                session.id_verified = True
                session.save()
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'exams/verify_identity.html', {'session': session, 'exam': session.exam})


@login_required
@require_POST
def submit_exam(request, session_id):
    """Student: submit exam answers for grading."""
    session = get_object_or_404(ExamSession, id=session_id, student=request.user)

    if session.status != 'in_progress':
        messages.warning(request, 'This session is already closed.')
        return redirect('accounts:student_dashboard')

    # Grade the exam
    questions = session.exam.questions.all()
    score = 0
    total = 0
    for question in questions:
        selected = request.POST.get(f'q_{question.id}', '')
        is_correct = (selected == question.correct_answer)
        if is_correct:
            score += question.marks
        total += question.marks
        StudentAnswer.objects.update_or_create(
            session=session,
            question=question,
            defaults={'selected_option': selected, 'is_correct': is_correct},
        )

    # Determine final status
    viol_score = session.total_violation_score
    status = 'flagged' if viol_score > 50 else 'completed'

    session.score = score
    session.total_marks = total
    session.end_time = timezone.now()
    session.status = status
    session.save()

    # Generate integrity report
    generate_integrity_report(session)

    messages.success(request, f'Exam submitted! You scored {score}/{total}.')
    return redirect('reports:report_detail', session_id=session.id)
