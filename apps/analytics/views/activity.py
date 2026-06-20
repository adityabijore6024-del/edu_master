"""
apps/analytics/views/activity.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.courses.models import Enrollment
from apps.analytics.models import RecentlyViewed


@login_required
def activity_view(request):
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related("course__teacher__user", "course__category").order_by("-enrolled_at")

    recently_viewed = RecentlyViewed.objects.filter(
        student=request.user
    ).select_related("course")[:10]

    return render(
        request,
        "activity/index.html",
        {"enrollments": enrollments, "recently_viewed": recently_viewed},
    )
