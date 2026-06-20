"""
apps/analytics/models.py
Study-time tracking and leaderboard snapshot models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class StudySession(models.Model):
    """Records one continuous study session for time-tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="study_sessions"
    )
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="study_sessions",
    )
    lecture = models.ForeignKey(
        "courses.Lecture",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="study_sessions",
    )
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"StudySession({self.student.username}, {self.duration_seconds}s)"


class RecentlyViewed(models.Model):
    """Last-viewed course for the activity page."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recently_viewed"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="viewed_by"
    )
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.student.username} viewed {self.course.title}"


class LeaderboardEntry(models.Model):
    """Periodic leaderboard snapshot (recomputed via management command or Celery)."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leaderboard_entries"
    )
    rank = models.PositiveIntegerField()
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    avg_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tests_count = models.PositiveSmallIntegerField(default=0)
    computed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["rank"]
        get_latest_by = "computed_at"

    def __str__(self):
        return f"#{self.rank} – {self.student.display_name}"
