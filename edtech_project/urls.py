"""
EdTech Platform – Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Public landing
    path("", include("apps.courses.urls.landing")),

    # Auth (login, signup, logout, forgot-password)
    path("auth/", include("apps.accounts.urls")),

    # Student dashboard
    path("dashboard/", include("apps.courses.urls.dashboard")),

    # Courses
    path("courses/", include("apps.courses.urls.courses")),

    # Teachers
    path("teachers/", include("apps.courses.urls.teachers")),

    # Payment
    path("payment/", include("apps.courses.urls.payment")),

    # Lecture
    path("lecture/", include("apps.courses.urls.lecture")),

    # AI Doubt Solver
    path("ai-doubt/", include("apps.ai_doubt.urls")),

    # Tests & Results
    path("tests/", include("apps.tests.urls")),

    # Activity
    path("activity/", include("apps.analytics.urls.activity")),

    # Analytics dashboard
    path("analytics/", include("apps.analytics.urls.analytics")),

    # Profile
    path("profile/", include("apps.accounts.urls_profile")),

    # Contact & Support
    path("support/", include("apps.accounts.urls_support")),

    # Leaderboard
    path("leaderboard/", include("apps.analytics.urls.leaderboard")),

    # Achievements
    path("achievements/", include("apps.achievements.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
