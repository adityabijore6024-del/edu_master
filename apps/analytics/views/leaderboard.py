"""
apps/analytics/views/leaderboard.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Count
from apps.tests.models import TestAttempt


@login_required
def leaderboard_view(request):
    # Compute leaderboard on the fly (small dataset; cache with Redis in production)
    rows = (
        TestAttempt.objects.filter(status__in=["submitted", "auto_submitted"])
        .values("student__id", "student__full_name", "student__username", "student__profile_photo")
        .annotate(
            total_score=Sum("score"),
            avg_pct=Avg("score"),
            tests_count=Count("id"),
        )
        .order_by("-total_score")[:50]
    )

    # Find current user's position
    user_rank = None
    for idx, row in enumerate(rows, start=1):
        if str(row["student__id"]) == str(request.user.id):
            user_rank = idx
            break

    return render(
        request,
        "leaderboard/index.html",
        {"rows": rows, "user_rank": user_rank},
    )
