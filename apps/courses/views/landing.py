"""
apps/courses/views/landing.py  — public landing page
"""
from django.shortcuts import render
from apps.courses.models import Course, Category, TeacherProfile, CourseRating


def landing_view(request):
    featured_courses = Course.objects.filter(is_active=True, is_featured=True).select_related(
        "teacher__user", "category"
    )[:6]
    categories = Category.objects.filter(is_active=True)[:8]
    teachers = TeacherProfile.objects.filter(is_featured=True).select_related("user")[:6]
    testimonials = CourseRating.objects.filter(stars__gte=4).select_related(
        "student", "course"
    )[:6]

    stats = {
        "students": 15000,
        "courses": Course.objects.filter(is_active=True).count() or 120,
        "teachers": TeacherProfile.objects.count() or 40,
        "success_rate": 94,
    }

    return render(
        request,
        "landing/index.html",
        {
            "featured_courses": featured_courses,
            "categories": categories,
            "teachers": teachers,
            "testimonials": testimonials,
            "stats": stats,
        },
    )
