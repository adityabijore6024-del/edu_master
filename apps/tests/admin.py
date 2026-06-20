"""apps/tests/admin.py"""
from django.contrib import admin
from .models import Test, Question, QuestionOption, TestAttempt, QuestionResponse


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 4
    max_num = 6


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_short", "test", "question_type", "marks", "order")
    list_filter = ("question_type", "test")
    search_fields = ("text",)
    inlines = [QuestionOptionInline]

    def text_short(self, obj):
        return obj.text[:60]
    text_short.short_description = "Question"


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ("text", "question_type", "marks", "order")
    show_change_link = True


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "duration_minutes", "total_marks", "is_active", "unlimited_attempts")
    list_filter = ("is_active", "unlimited_attempts", "course")
    search_fields = ("title",)
    inlines = [QuestionInline]
    readonly_fields = ("id", "created_at")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "test", "status", "score", "percentage", "started_at")
    list_filter = ("status", "test")
    search_fields = ("student__email", "test__title")
    readonly_fields = ("id", "started_at", "submitted_at")


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct", "is_skipped", "marks_awarded")
    list_filter = ("is_correct", "is_skipped")
