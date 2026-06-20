"""apps/analytics/urls/activity.py"""
from django.urls import path
from apps.analytics.views.activity import activity_view

urlpatterns = [
    path("", activity_view, name="activity"),
]
