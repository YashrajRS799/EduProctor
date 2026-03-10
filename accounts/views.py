"""
Accounts app views – Authentication and dashboards.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone

from .forms import LoginForm, RegisterForm
from exams.models import Exam, ExamSession


def login_view(request):
    """Handle user login with role-based redirect."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


def redirect_by_role(user):
    """Redirect user based on their role."""
    from django.shortcuts import redirect
    if user.is_admin_user:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:student_dashboard')


def register_view(request):
    """Handle new user registration."""
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}.')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    """Log the user out."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def dashboard_redirect(request):
    """Smart redirect to the appropriate dashboard."""
    return redirect_by_role(request.user)


@login_required
def admin_dashboard(request):
    """Admin dashboard – overview of exams, sessions, violations."""
    if not request.user.is_admin_user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:student_dashboard')

    exams = Exam.objects.filter(created_by=request.user).annotate(
        session_count=Count('sessions')
    ).order_by('-created_at')

    recent_sessions = ExamSession.objects.filter(
        exam__created_by=request.user
    ).select_related('student', 'exam').order_by('-start_time')[:10]

    # Stats
    total_students = ExamSession.objects.filter(
        exam__created_by=request.user
    ).values('student').distinct().count()

    flagged_sessions = ExamSession.objects.filter(
        exam__created_by=request.user,
        status='flagged'
    ).count()

    context = {
        'exams': exams,
        'recent_sessions': recent_sessions,
        'total_exams': exams.count(),
        'total_students': total_students,
        'flagged_sessions': flagged_sessions,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def student_dashboard(request):
    """Student dashboard – available exams and past attempts."""
    if not request.user.is_student_user:
        messages.error(request, 'Access denied.')
        return redirect('accounts:admin_dashboard')

    now = timezone.now()

    # Exams available right now
    available_exams = Exam.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now,
    ).exclude(
        sessions__student=request.user,
        sessions__status__in=['completed', 'flagged', 'timed_out'],
    )

    # Upcoming exams
    upcoming_exams = Exam.objects.filter(
        is_active=True,
        start_time__gt=now,
    )

    # Completed sessions
    completed_sessions = ExamSession.objects.filter(
        student=request.user,
    ).select_related('exam').order_by('-start_time')

    context = {
        'available_exams': available_exams,
        'upcoming_exams': upcoming_exams,
        'completed_sessions': completed_sessions,
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def system_info(request):
    """View to display project objectives and limitations."""
    return render(request, 'accounts/system_info.html')
