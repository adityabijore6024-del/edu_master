"""
apps/courses/views/dashboard.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course, Category, Enrollment
from apps.analytics.models import RecentlyViewed


@login_required
def dashboard_view(request):
    query = request.GET.get("q", "").strip()
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related("course__teacher__user", "course__category")

    all_courses = Course.objects.filter(is_active=True)
    if query:
        all_courses = all_courses.filter(title__icontains=query)

    featured_courses = all_courses.filter(is_featured=True)[:6]
    categories = Category.objects.filter(is_active=True)

    recently_viewed = RecentlyViewed.objects.filter(
        student=request.user
    ).select_related("course")[:6]

    return render(
        request,
        "dashboard/home.html",
        {
            "enrollments": enrollments,
            "featured_courses": featured_courses,
            "categories": categories,
            "recently_viewed": recently_viewed,
            "query": query,
        },
    )
