"""
apps/tests/models.py
Test, Question (single / multiple / integer), and Attempt models.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Test(models.Model):
    """Quiz / exam associated with a course section or standalone."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)

    # A test may belong to a course (optional – can be standalone)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tests",
    )
    lecture = models.ForeignKey(
        "courses.Lecture",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tests",
    )

    duration_minutes = models.PositiveSmallIntegerField(
        default=30, help_text="Total time allowed in minutes (0 = unlimited)"
    )
    total_marks = models.PositiveSmallIntegerField(default=0)
    passing_marks = models.PositiveSmallIntegerField(default=0)
    negative_marks = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    unlimited_attempts = models.BooleanField(default=True)
    max_attempts = models.PositiveSmallIntegerField(
        default=0, help_text="0 = unlimited"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    """A single question inside a test."""

    class QuestionType(models.TextChoices):
        SINGLE = "single", _("Single Correct")
        MULTIPLE = "multiple", _("Multiple Correct")
        INTEGER = "integer", _("Integer / Numerical")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(help_text="Question statement (supports HTML / LaTeX)")
    question_type = models.CharField(
        max_length=10, choices=QuestionType.choices, default=QuestionType.SINGLE
    )
    image = models.ImageField(upload_to="questions/%Y/%m/", blank=True, null=True)
    marks = models.PositiveSmallIntegerField(default=4)
    negative_marks = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    explanation = models.TextField(blank=True, help_text="Solution shown after submission")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class QuestionOption(models.Model):
    """One option (A/B/C/D) for a question."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    label = models.CharField(max_length=1, help_text="A, B, C, D …")
    text = models.TextField()
    image = models.ImageField(upload_to="options/%Y/%m/", blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["label"]
        unique_together = ("question", "label")

    def __str__(self):
        return f"Option {self.label} – {'✓' if self.is_correct else '✗'}"


class TestAttempt(models.Model):
    """One sitting of a test by a student."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", _("In Progress")
        SUBMITTED = "submitted", _("Submitted")
        AUTO_SUBMITTED = "auto_submitted", _("Auto Submitted (time-out)")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_attempts"
    )
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(default=0)

    score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total_marks = models.PositiveSmallIntegerField(default=0)
    correct_count = models.PositiveSmallIntegerField(default=0)
    wrong_count = models.PositiveSmallIntegerField(default=0)
    skipped_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} – {self.test.title} [{self.status}]"

    @property
    def percentage(self):
        if self.total_marks:
            return round((float(self.score) / self.total_marks) * 100, 2)
        return 0


class QuestionResponse(models.Model):
    """Student's answer to one question in an attempt."""

    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="responses")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="responses")

    # For single/multiple: store selected option labels as comma-separated e.g. "A,C"
    selected_options = models.CharField(max_length=20, blank=True)
    # For integer questions
    integer_answer = models.IntegerField(null=True, blank=True)

    is_correct = models.BooleanField(default=False)
    marks_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_skipped = models.BooleanField(default=True)

    class Meta:
        unique_together = ("attempt", "question")

    def __str__(self):
        return f"Response – {self.question}"
