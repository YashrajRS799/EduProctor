"""Exams admin registration."""
from django.contrib import admin
from .models import Exam, Question, ExamSession, StudentAnswer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'duration_minutes', 'is_active', 'start_time', 'end_time']
    list_filter = ['is_active', 'created_by']
    inlines = [QuestionInline]


@admin.register(ExamSession)
class ExamSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'status', 'score', 'total_marks', 'total_violation_score', 'start_time']
    list_filter = ['status', 'exam']


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['session', 'question', 'selected_option', 'is_correct']
