"""apps/achievements/admin.py"""
from django.contrib import admin
from .models import Badge, StudentBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "tier", "require_tests_count", "require_min_score_pct", "is_active", "order")
    list_filter = ("tier", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("id",)


@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ("student", "badge", "awarded_at")
    list_filter = ("badge",)
    search_fields = ("student__email",)
    readonly_fields = ("id", "awarded_at")
