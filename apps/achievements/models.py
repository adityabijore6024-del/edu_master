"""
apps/achievements/models.py
Badge definition and student-badge award models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Badge(models.Model):
    """A reusable achievement badge definition."""

    class Tier(models.TextChoices):
        BRONZE = "bronze", _("Bronze")
        SILVER = "silver", _("Silver")
        GOLD = "gold", _("Gold")
        PLATINUM = "platinum", _("Platinum")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.CharField(max_length=300)
    icon = models.CharField(max_length=50, default="bi-award", help_text="Bootstrap icon class")
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.BRONZE)

    # Trigger conditions (simple numeric thresholds)
    require_tests_count = models.PositiveSmallIntegerField(
        default=0, help_text="Number of tests submitted to unlock (0 = not used)"
    )
    require_min_score_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Minimum percentage in any single test (0 = not used)"
    )
    require_courses_count = models.PositiveSmallIntegerField(
        default=0, help_text="Number of courses enrolled (0 = not used)"
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "tier"]

    def __str__(self):
        return f"{self.name} [{self.tier}]"


# Seed data for badges (used in a migration or management command)
INITIAL_BADGES = [
    {
        "name": "First Step",
        "slug": "first-step",
        "description": "Submitted your first test.",
        "icon": "bi-flag",
        "tier": Badge.Tier.BRONZE,
        "require_tests_count": 1,
    },
    {
        "name": "Test Veteran",
        "slug": "test-veteran",
        "description": "Completed 10 tests.",
        "icon": "bi-journal-check",
        "tier": Badge.Tier.SILVER,
        "require_tests_count": 10,
    },
    {
        "name": "High Achiever",
        "slug": "high-achiever",
        "description": "Scored 90% or above in a test.",
        "icon": "bi-star-fill",
        "tier": Badge.Tier.GOLD,
        "require_min_score_pct": 90,
    },
    {
        "name": "Master Rank",
        "slug": "master-rank",
        "description": "Completed 25 tests with an average above 80%.",
        "icon": "bi-trophy-fill",
        "tier": Badge.Tier.PLATINUM,
        "require_tests_count": 25,
        "require_min_score_pct": 80,
    },
]


class StudentBadge(models.Model):
    """Association: a specific student has earned a specific badge."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="badges"
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name="awarded_to")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "badge")
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"{self.student.display_name} earned {self.badge.name}"
