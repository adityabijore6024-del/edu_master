"""apps/courses/urls/courses.py"""
from django.urls import path
from apps.courses.views.courses import courses_list_view, course_detail_view

urlpatterns = [
    path("", courses_list_view, name="courses_list"),
    path("<slug:slug>/", course_detail_view, name="course_detail"),
]
