"""
apps/courses/views/teachers.py
"""
from django.shortcuts import render, get_object_or_404
from apps.courses.models import TeacherProfile


def teachers_list_view(request):
    teachers = TeacherProfile.objects.select_related("user").prefetch_related("courses")
    return render(request, "teachers/list.html", {"teachers": teachers})


def teacher_detail_view(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    courses = teacher.courses.filter(is_active=True)
    return render(request, "teachers/detail.html", {"teacher": teacher, "courses": courses})
