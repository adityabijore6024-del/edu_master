"""apps/courses/urls/lecture.py"""
from django.urls import path
from apps.courses.views.lecture import lecture_list_view, lecture_detail_view

urlpatterns = [
    path("<slug:slug>/", lecture_list_view, name="lecture_list"),
    path("<slug:slug>/<uuid:lecture_id>/", lecture_detail_view, name="lecture_detail"),
]
