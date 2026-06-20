"""apps/analytics/admin.py"""
from django.contrib import admin
from .models import StudySession, RecentlyViewed, LeaderboardEntry


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "lecture", "duration_seconds", "started_at")
    list_filter = ("started_at",)
    readonly_fields = ("id",)


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "viewed_at")
    list_filter = ("viewed_at",)


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ("rank", "student", "total_score", "avg_percentage", "tests_count", "computed_at")
    list_filter = ("computed_at",)
    ordering = ("rank",)
