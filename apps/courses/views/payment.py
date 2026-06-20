"""
apps/courses/views/payment.py
Razorpay order creation + webhook verification.
"""
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings

from apps.courses.models import Course, Enrollment, Payment


@login_required
def payment_page_view(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)

    # Redirect if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect("lecture_list", slug=slug)

    benefits = [
        "Lifetime access to all lectures",
        "Downloadable notes & assignments",
        "Unlimited test attempts",
        "AI Doubt Solver access",
        "Certificate on completion",
        "Mobile & desktop access",
    ]
    return render(
        request,
        "payment/checkout.html",
        {
            "course": course,
            "benefits": benefits,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
        },
    )


@login_required
@require_POST
def create_razorpay_order(request):
    """Create a Razorpay order and return order_id to the frontend."""
    import razorpay

    data = json.loads(request.body)
    course_id = data.get("course_id")
    course = get_object_or_404(Course, id=course_id, is_active=True)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(course.price * 100)

    order = client.order.create(
        {"amount": amount_paise, "currency": "INR", "payment_capture": 1}
    )

    # Create a pending enrollment + payment record
    enrollment, _ = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={"amount_paid": course.price, "razorpay_order_id": order["id"]},
    )
    Payment.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "razorpay_order_id": order["id"],
            "amount": course.price,
        },
    )

    return JsonResponse(
        {
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "course_name": course.title,
        }
    )


@login_required
@require_POST
def verify_payment(request):
    """Verify Razorpay signature and activate enrollment."""
    import razorpay

    data = json.loads(request.body)
    razorpay_order_id = data.get("razorpay_order_id", "")
    razorpay_payment_id = data.get("razorpay_payment_id", "")
    razorpay_signature = data.get("razorpay_signature", "")

    # Signature verification
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"success": False, "error": "Signature verification failed."}, status=400)

    # Update DB
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = Payment.Status.CAPTURED
        payment.save()

        enrollment = payment.enrollment
        enrollment.is_active = True
        enrollment.razorpay_payment_id = razorpay_payment_id
        enrollment.save()

        # Bump student count
        course = enrollment.course
        course.total_students = course.enrollments.filter(is_active=True).count()
        course.save(update_fields=["total_students"])

    except Payment.DoesNotExist:
        return JsonResponse({"success": False, "error": "Payment record not found."}, status=404)

    return JsonResponse({"success": True, "redirect": f"/lecture/{enrollment.course.slug}/"})


def payment_success_view(request):
    return render(request, "payment/success.html")
