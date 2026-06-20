"""apps/courses/urls/teachers.py"""
from django.urls import path
from apps.courses.views.teachers import teachers_list_view, teacher_detail_view

urlpatterns = [
    path("", teachers_list_view, name="teachers_list"),
    path("<int:pk>/", teacher_detail_view, name="teacher_detail"),
]
