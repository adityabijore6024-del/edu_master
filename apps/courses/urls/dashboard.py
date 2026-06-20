"""apps/courses/urls/dashboard.py"""
from django.urls import path
from apps.courses.views.dashboard import dashboard_view

urlpatterns = [
    path("", dashboard_view, name="dashboard"),
]
