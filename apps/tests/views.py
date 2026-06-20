"""
apps/tests/views.py
Test list, active test session, submit, and result views.
"""
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Test, TestAttempt, QuestionResponse, Question


@login_required
def test_list_view(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, "tests/list.html", {"tests": tests})


@login_required
def test_start_view(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)

    # Check attempt limits
    if not test.unlimited_attempts and test.max_attempts:
        attempt_count = TestAttempt.objects.filter(
            student=request.user, test=test
        ).exclude(status="in_progress").count()
        if attempt_count >= test.max_attempts:
            return render(request, "tests/limit_reached.html", {"test": test})

    # Create new attempt
    attempt = TestAttempt.objects.create(
        student=request.user,
        test=test,
        total_marks=test.total_marks or sum(q.marks for q in test.questions.all()),
    )

    questions = test.questions.prefetch_related("options")
    return render(
        request,
        "tests/active.html",
        {
            "test": test,
            "attempt": attempt,
            "questions": questions,
            "duration_seconds": test.duration_minutes * 60,
        },
    )


@login_required
@require_POST
def submit_test_view(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)

    if attempt.status != "in_progress":
        return redirect("test_result", attempt_id=attempt_id)

    data = json.loads(request.body)
    answers = data.get("answers", {})  # {question_id: [option_labels] or integer}
    time_taken = data.get("time_taken", 0)

    total_score = 0
    correct = wrong = skipped = 0

    for question in attempt.test.questions.prefetch_related("options"):
        q_id = str(question.id)
        raw_answer = answers.get(q_id)
        is_skipped = raw_answer is None

        response_obj, _ = QuestionResponse.objects.get_or_create(
            attempt=attempt, question=question
        )
        response_obj.is_skipped = is_skipped

        if is_skipped:
            skipped += 1
            response_obj.marks_awarded = 0
        elif question.question_type == Question.QuestionType.INTEGER:
            try:
                int_ans = int(raw_answer)
            except (ValueError, TypeError):
                int_ans = None
            response_obj.integer_answer = int_ans
            correct_int = question.options.filter(is_correct=True).first()
            is_correct = correct_int and str(int_ans) == correct_int.text
            response_obj.is_correct = bool(is_correct)
            if is_correct:
                response_obj.marks_awarded = question.marks
                correct += 1
                total_score += question.marks
            else:
                response_obj.marks_awarded = -float(question.negative_marks)
                total_score -= float(question.negative_marks)
                wrong += 1
        else:
            selected = set(raw_answer) if isinstance(raw_answer, list) else {raw_answer}
            response_obj.selected_options = ",".join(sorted(selected))
            correct_labels = set(
                question.options.filter(is_correct=True).values_list("label", flat=True)
            )
            is_correct = selected == correct_labels
            response_obj.is_correct = is_correct
            if is_correct:
                response_obj.marks_awarded = question.marks
                correct += 1
                total_score += question.marks
            else:
                response_obj.marks_awarded = -float(question.negative_marks)
                total_score -= float(question.negative_marks)
                wrong += 1

        response_obj.save()

    attempt.score = max(total_score, 0)
    attempt.correct_count = correct
    attempt.wrong_count = wrong
    attempt.skipped_count = skipped
    attempt.time_taken_seconds = time_taken
    attempt.status = TestAttempt.Status.SUBMITTED
    attempt.submitted_at = timezone.now()
    attempt.save()

    # Check / award badges
    _check_and_award_badges(request.user, attempt)

    return JsonResponse({"success": True, "redirect": f"/tests/result/{attempt_id}/"})


@login_required
def test_result_view(request, attempt_id):
    attempt = get_object_or_404(TestAttempt, id=attempt_id, student=request.user)
    responses = attempt.responses.select_related("question").prefetch_related(
        "question__options"
    )
    return render(
        request,
        "tests/result.html",
        {"attempt": attempt, "responses": responses},
    )


def _check_and_award_badges(user, attempt):
    """Award badges based on the latest attempt stats."""
    from apps.achievements.models import Badge, StudentBadge

    submitted_count = TestAttempt.objects.filter(
        student=user, status__in=["submitted", "auto_submitted"]
    ).count()

    badges = Badge.objects.filter(is_active=True)
    for badge in badges:
        earned = False
        if badge.require_tests_count and submitted_count >= badge.require_tests_count:
            earned = True
        if badge.require_min_score_pct and attempt.percentage >= float(badge.require_min_score_pct):
            earned = True

        if earned:
            StudentBadge.objects.get_or_create(student=user, badge=badge)
