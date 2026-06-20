"""apps/courses/admin.py"""
from django.contrib import admin
from .models import (
    Category, TeacherProfile, Course, CourseSection, Lecture,
    Enrollment, LectureProgress, CourseRating, Payment,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "order")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "order")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "designation", "total_students", "is_featured", "order")
    list_filter = ("is_featured",)
    search_fields = ("user__email", "user__full_name", "designation")


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title", "teacher", "category", "price", "is_active",
        "is_featured", "total_students", "avg_rating", "created_at",
    )
    list_filter = ("is_active", "is_featured", "category", "difficulty", "language")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseSectionInline]
    readonly_fields = ("id", "created_at", "updated_at", "total_students", "avg_rating", "total_ratings")

    fieldsets = (
        ("Basic Info", {"fields": ("title", "slug", "teacher", "category", "thumbnail", "promo_video_url")}),
        ("Description", {"fields": ("short_description", "description", "what_you_learn", "requirements")}),
        ("Pricing", {"fields": ("original_price", "discounted_price", "is_free")}),
        ("Settings", {"fields": ("language", "difficulty", "is_active", "is_featured")}),
        ("Stats", {"fields": ("total_students", "avg_rating", "total_ratings")}),
        ("Timestamps", {"fields": ("id", "created_at", "updated_at")}),
    )


class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [LectureInline]


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "content_type", "duration_minutes", "is_preview", "order")
    list_filter = ("content_type", "is_preview")
    search_fields = ("title",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "amount_paid", "is_active")
    list_filter = ("is_active", "enrolled_at")
    search_fields = ("student__email", "course__title")
    readonly_fields = ("id", "enrolled_at")


@admin.register(LectureProgress)
class LectureProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lecture", "completed", "last_watched")
    list_filter = ("completed",)


@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "stars", "created_at")
    list_filter = ("stars",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("razorpay_order_id", "amount", "status", "created_at")
    list_filter = ("status", "currency")
    readonly_fields = ("id", "created_at")
