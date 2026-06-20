"""apps/ai_doubt/admin.py"""
from django.contrib import admin
from .models import DoubtSession, DoubtMessage


class DoubtMessageInline(admin.TabularInline):
    model = DoubtMessage
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


@admin.register(DoubtSession)
class DoubtSessionAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "course", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("student__email", "title")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [DoubtMessageInline]


@admin.register(DoubtMessage)
class DoubtMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "content_short", "created_at")
    list_filter = ("role",)
    readonly_fields = ("id", "created_at")

    def content_short(self, obj):
        return obj.content[:80]
    content_short.short_description = "Content"
