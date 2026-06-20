"""
apps/analytics/views/analytics.py
"""
import json
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Avg, Max, Count
from apps.courses.models import Enrollment
from apps.tests.models import TestAttempt
from apps.analytics.models import StudySession


class DjangoJSONEncoder(json.JSONEncoder):
    """Handles Decimal and datetime serialization for chart data."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super().default(obj)


@login_required
def analytics_dashboard_view(request):
    user = request.user

    enrollments_count = Enrollment.objects.filter(student=user, is_active=True).count()
    attempts = TestAttempt.objects.filter(
        student=user, status__in=["submitted", "auto_submitted"]
    )
    tests_count = attempts.count()
    best_score = attempts.aggregate(best=Max("score"))["best"] or 0
    avg_pct = attempts.aggregate(avg=Avg("score"))["avg"] or 0
    total_study_seconds = (
        StudySession.objects.filter(student=user).aggregate(total=Sum("duration_seconds"))["total"] or 0
    )
    total_study_hours = round(total_study_seconds / 3600, 1)

    # Per-test data for chart
    chart_data_raw = list(
        attempts.order_by("started_at").values("test__title", "score", "started_at")[:20]
    )
    chart_data = json.dumps(chart_data_raw, cls=DjangoJSONEncoder)

    return render(
        request,
        "analytics/dashboard.html",
        {
            "enrollments_count": enrollments_count,
            "tests_count": tests_count,
            "best_score": best_score,
            "avg_pct": round(float(avg_pct), 1),
            "total_study_hours": total_study_hours,
            "chart_data": chart_data,
        },
    )
