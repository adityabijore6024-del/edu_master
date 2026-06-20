"""apps/achievements/views.py"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Badge, StudentBadge


@login_required
def achievements_view(request):
    all_badges = Badge.objects.filter(is_active=True)
    earned_ids = set(
        StudentBadge.objects.filter(student=request.user).values_list("badge_id", flat=True)
    )
    return render(
        request,
        "achievements/index.html",
        {"all_badges": all_badges, "earned_ids": earned_ids},
    )
