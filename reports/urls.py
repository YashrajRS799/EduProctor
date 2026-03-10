"""Reports app URL configuration."""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('session/<int:session_id>/', views.report_detail, name='report_detail'),
    path('list/', views.report_list, name='report_list'),
    path('export/', views.export_report_csv, name='export_csv'),
]
