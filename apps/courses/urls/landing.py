"""apps/courses/urls/landing.py"""
from django.urls import path
from apps.courses.views.landing import landing_view

urlpatterns = [
    path("", landing_view, name="landing"),
]
