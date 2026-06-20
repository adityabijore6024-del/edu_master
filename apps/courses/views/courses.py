"""
apps/courses/views/courses.py
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.courses.models import Course, Category, Enrollment
from apps.analytics.models import RecentlyViewed


def courses_list_view(request):
    courses = Course.objects.filter(is_active=True).select_related(
        "teacher__user", "category"
    )
    category_slug = request.GET.get("category", "")
    query = request.GET.get("q", "").strip()
    level = request.GET.get("level", "")

    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if query:
        courses = courses.filter(title__icontains=query)
    if level:
        courses = courses.filter(difficulty=level)

    categories = Category.objects.filter(is_active=True)
    return render(
        request,
        "courses/list.html",
        {
            "courses": courses,
            "categories": categories,
            "selected_category": category_slug,
            "query": query,
            "level": level,
        },
    )


def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Track recently viewed
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            student=request.user, course=course
        )

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course, is_active=True
        ).exists()

    sections = course.sections.prefetch_related("lectures")
    ratings = course.ratings.select_related("student")[:10]

    return render(
        request,
        "courses/detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "sections": sections,
            "ratings": ratings,
        },
    )
