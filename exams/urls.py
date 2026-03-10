"""Exams app URL configuration."""
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Admin
    path('', views.exam_list, name='exam_list'),
    path('create/', views.create_exam, name='create_exam'),
    path('<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('<int:exam_id>/questions/', views.add_questions, name='add_questions'),
    path('<int:exam_id>/detail/', views.exam_detail, name='exam_detail'),
    # Student
    path('available/', views.student_exam_list, name='student_exam_list'),
    path('<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('session/<int:session_id>/verify/', views.verify_identity, name='verify_identity'),
    path('session/<int:session_id>/submit/', views.submit_exam, name='submit_exam'),
]
