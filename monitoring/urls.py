"""Monitoring app URL configuration."""
from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('log/', views.log_violation, name='log_violation'),
    path('webcam-status/', views.webcam_status, name='webcam_status'),
]
