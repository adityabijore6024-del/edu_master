"""apps/analytics/urls/leaderboard.py"""
from django.urls import path
from apps.analytics.views.leaderboard import leaderboard_view

urlpatterns = [
    path("", leaderboard_view, name="leaderboard"),
]
