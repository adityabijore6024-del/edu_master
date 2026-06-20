"""
apps/accounts/views.py
Signup, Login, Logout, Forgot / Reset Password, Profile, Support views.
"""
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import User, PasswordResetToken, SupportTicket
from .forms import (
    SignupForm, LoginForm, ForgotPasswordForm,
    ResetPasswordForm, ProfileUpdateForm, SupportTicketForm,
)


# ─── Authentication ──────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome to EduPeak, {user.display_name}! 🎉")
        return redirect("dashboard")
    return render(request, "auth/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user and user.is_active:
            login(request, user)
            next_url = request.GET.get("next", "dashboard")
            messages.success(request, f"Welcome back, {user.display_name}!")
            return redirect(next_url)
        messages.error(request, "Invalid credentials. Please try again.")
    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out successfully.")
    return redirect("landing")


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timezone.timedelta(hours=1),
            )
            reset_link = request.build_absolute_uri(
                f"/auth/reset-password/{token.token}/"
            )
            send_mail(
                subject="Reset your EduPeak password",
                message=f"Click the link below to reset your password:\n\n{reset_link}\n\nThis link expires in 1 hour.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Don't leak user existence
        messages.success(
            request,
            "If that email is registered, you'll receive a reset link shortly.",
        )
        return redirect("login")
    return render(request, "auth/forgot_password.html", {"form": form})


def reset_password_view(request, token):
    token_obj = get_object_or_404(PasswordResetToken, token=token)
    if not token_obj.is_valid():
        messages.error(request, "This reset link has expired or already been used.")
        return redirect("forgot_password")

    form = ResetPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        token_obj.user.set_password(form.cleaned_data["password"])
        token_obj.user.save()
        token_obj.used = True
        token_obj.save()
        messages.success(request, "Password updated! Please log in.")
        return redirect("login")
    return render(request, "auth/reset_password.html", {"form": form, "token": token})


# ─── Profile ─────────────────────────────────────────────────

@login_required
def profile_view(request):
    from apps.courses.models import Enrollment
    from apps.tests.models import TestAttempt

    enrollments = Enrollment.objects.filter(student=request.user).select_related("course")
    attempts = TestAttempt.objects.filter(
        student=request.user, status__in=["submitted", "auto_submitted"]
    ).count()

    context = {
        "enrollments": enrollments,
        "attempts_count": attempts,
    }
    return render(request, "profile/profile.html", context)


@login_required
def profile_edit_view(request):
    form = ProfileUpdateForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "profile/edit.html", {"form": form})


# ─── Support ─────────────────────────────────────────────────

def support_view(request):
    form = SupportTicketForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ticket = form.save(commit=False)
        if request.user.is_authenticated:
            ticket.user = request.user
        ticket.save()
        # Send notification email
        send_mail(
            subject=f"[EduPeak Support] New Ticket: {ticket.subject}",
            message=f"From: {ticket.name} <{ticket.email}>\n\n{ticket.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.SUPPORT_EMAIL],
            fail_silently=True,
        )
        messages.success(request, "Your query has been submitted. We'll get back to you within 24 hours.")
        return redirect("support")

    faqs = [
        {
            "q": "How do I enroll in a course?",
            "a": "Browse courses, click 'Enroll Now', and complete the payment via Razorpay.",
        },
        {
            "q": "Can I access lectures offline?",
            "a": "Currently, lectures are available online. Download of notes PDFs is supported.",
        },
        {
            "q": "How does the AI Doubt Solver work?",
            "a": "Ask any academic question in the chat and our AI tutor powered by Claude will answer instantly.",
        },
        {
            "q": "Are there refunds?",
            "a": "Refunds are processed within 7 days if you haven't accessed more than 20% of the course.",
        },
        {
            "q": "How many times can I attempt a test?",
            "a": "Most tests allow unlimited attempts so you can practice freely.",
        },
    ]
    return render(
        request,
        "contact/support.html",
        {
            "form": form,
            "faqs": faqs,
            "whatsapp": settings.WHATSAPP_NUMBER,
            "support_email": settings.SUPPORT_EMAIL,
        },
    )
