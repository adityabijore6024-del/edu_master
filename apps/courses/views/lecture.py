"""
apps/courses/views/lecture.py
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.courses.models import Course, Enrollment, Lecture, LectureProgress


@login_required
def lecture_list_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Enforce enrollment
    if not Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.warning(request, "Please enroll to access this course.")
        return redirect("course_detail", slug=slug)

    sections = course.sections.prefetch_related("lectures")

    # Get completed lecture IDs for progress tracking
    completed_ids = set(
        LectureProgress.objects.filter(
            student=request.user, completed=True, lecture__section__course=course
        ).values_list("lecture_id", flat=True)
    )

    return render(
        request,
        "lecture/list.html",
        {"course": course, "sections": sections, "completed_ids": completed_ids},
    )


@login_required
def lecture_detail_view(request, slug, lecture_id):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    lecture = get_object_or_404(Lecture, id=lecture_id, section__course=course)

    if not (
        lecture.is_preview
        or Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()
    ):
        messages.warning(request, "Please enroll to access this lecture.")
        return redirect("course_detail", slug=slug)

    # Mark as seen
    progress, _ = LectureProgress.objects.get_or_create(
        student=request.user, lecture=lecture
    )
    progress.completed = True
    progress.save()

    # Get adjacent lectures for navigation
    all_lectures = list(
        Lecture.objects.filter(section__course=course).order_by("section__order", "order")
    )
    current_idx = next((i for i, l in enumerate(all_lectures) if str(l.id) == str(lecture.id)), 0)
    prev_lecture = all_lectures[current_idx - 1] if current_idx > 0 else None
    next_lecture = all_lectures[current_idx + 1] if current_idx < len(all_lectures) - 1 else None

    # Related tests
    related_tests = lecture.tests.filter(is_active=True)

    return render(
        request,
        "lecture/detail.html",
        {
            "course": course,
            "lecture": lecture,
            "prev_lecture": prev_lecture,
            "next_lecture": next_lecture,
            "related_tests": related_tests,
        },
    )
