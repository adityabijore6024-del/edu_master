"""
apps/courses/models.py
Category, Teacher, Course, Enrollment, Lecture, Rating, and Watchlist models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Category(models.Model):
    """Top-level subject grouping (e.g. Mathematics, Physics)."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class, e.g. bi-calculator")
    color = models.CharField(max_length=7, default="#6366f1", help_text="Hex colour for card accent")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TeacherProfile(models.Model):
    """Extended profile for teacher-role users."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )
    photo = models.ImageField(upload_to="teachers/%Y/%m/", blank=True, null=True)
    designation = models.CharField(max_length=150, blank=True, help_text="e.g. IIT Delhi, 10 yrs experience")
    subjects = models.CharField(max_length=300, blank=True)
    youtube_url = models.URLField(blank=True)
    total_students = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "user__full_name"]

    def __str__(self):
        return f"Teacher – {self.user.display_name}"


class Course(models.Model):
    """The central content unit."""

    class DifficultyLevel(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        ADVANCED = "advanced", _("Advanced")

    class Language(models.TextChoices):
        HINDI = "hindi", _("Hindi")
        ENGLISH = "english", _("English")
        HINGLISH = "hinglish", _("Hinglish")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)

    teacher = models.ForeignKey(
        TeacherProfile, on_delete=models.CASCADE, related_name="courses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="courses"
    )

    thumbnail = models.ImageField(upload_to="courses/%Y/%m/", blank=True, null=True)
    promo_video_url = models.URLField(blank=True)

    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)

    language = models.CharField(max_length=10, choices=Language.choices, default=Language.HINGLISH)
    difficulty = models.CharField(
        max_length=15, choices=DifficultyLevel.choices, default=DifficultyLevel.BEGINNER
    )

    what_you_learn = models.TextField(blank=True, help_text="Newline-separated list of outcomes")
    requirements = models.TextField(blank=True, help_text="Newline-separated prerequisites")

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    total_students = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def price(self):
        """Effective purchase price."""
        return self.discounted_price if self.discounted_price else self.original_price

    @property
    def discount_percentage(self):
        if self.original_price and self.discounted_price:
            return int(100 - (self.discounted_price / self.original_price * 100))
        return 0

    @property
    def what_you_learn_list(self):
        return [line.strip() for line in self.what_you_learn.splitlines() if line.strip()]

    @property
    def requirements_list(self):
        return [line.strip() for line in self.requirements.splitlines() if line.strip()]


class CourseSection(models.Model):
    """Chapter / module grouping for lectures."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} › {self.title}"


class Lecture(models.Model):
    """Individual content item (video / notes / assignment / quiz)."""

    class ContentType(models.TextChoices):
        VIDEO = "video", _("Video")
        NOTES = "notes", _("Notes / PDF")
        ASSIGNMENT = "assignment", _("Assignment")
        TEST = "test", _("Test")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=250)
    content_type = models.CharField(max_length=15, choices=ContentType.choices, default=ContentType.VIDEO)
    video_url = models.URLField(blank=True)
    notes_file = models.FileField(upload_to="notes/%Y/%m/", blank=True, null=True)
    duration_minutes = models.PositiveSmallIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Accessible without enrollment")
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.section} › {self.title}"


class Enrollment(models.Model):
    """Student ↔ Course relationship after purchase."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.display_name} → {self.course.title}"


class LectureProgress(models.Model):
    """Tracks which lectures a student has watched."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lecture_progress"
    )
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="progress_records")
    completed = models.BooleanField(default=False)
    watched_seconds = models.PositiveIntegerField(default=0)
    last_watched = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "lecture")

    def __str__(self):
        return f"{self.student.username} – {self.lecture.title}"


class CourseRating(models.Model):
    """Star rating + review for a course."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.username} rated {self.course.title}: {self.stars}★"


class Payment(models.Model):
    """Razorpay payment record."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CAPTURED = "captured", _("Captured")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name="payment")
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=256, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5, default="INR")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.razorpay_order_id} – {self.status}"
