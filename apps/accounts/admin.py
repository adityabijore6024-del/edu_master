"""apps/accounts/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken, SupportTicket


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "username", "full_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff", "email_verified")
    search_fields = ("email", "username", "full_name", "mobile")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "full_name", "mobile", "bio", "profile_photo")}),
        ("Role & Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "email_verified", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "username", "password1", "password2", "role")}),
    )
    readonly_fields = ("date_joined", "last_login")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at", "used")
    list_filter = ("used",)
    readonly_fields = ("token", "created_at")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "updated_at")
