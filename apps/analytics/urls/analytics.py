"""apps/analytics/urls/analytics.py"""
from django.urls import path
from apps.analytics.views.analytics import analytics_dashboard_view

urlpatterns = [
    path("", analytics_dashboard_view, name="analytics"),
]
