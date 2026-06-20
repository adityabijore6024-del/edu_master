"""
apps/accounts/models.py
Custom User model + OTP / password-reset token models.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom manager for email-based authentication."""

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Central user model.
    Authentication is done via email + password.
    """

    class Role(models.TextChoices):
        STUDENT = "student", _("Student")
        TEACHER = "teacher", _("Teacher")
        ADMIN = "admin", _("Admin")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=50, unique=True)
    full_name = models.CharField(_("full name"), max_length=150, blank=True)
    mobile = models.CharField(_("mobile number"), max_length=15, blank=True)
    role = models.CharField(_("role"), max_length=10, choices=Role.choices, default=Role.STUDENT)

    profile_photo = models.ImageField(
        _("profile photo"), upload_to="profiles/%Y/%m/", blank=True, null=True
    )
    bio = models.TextField(_("bio"), blank=True)

    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    email_verified = models.BooleanField(_("email verified"), default=False)

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    last_login = models.DateTimeField(_("last login"), blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    @property
    def display_name(self):
        return self.full_name or self.username

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class PasswordResetToken(models.Model):
    """Secure one-time token for password reset flow."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("password reset token")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"ResetToken({self.user.email}, valid={self.is_valid()})"


class SupportTicket(models.Model):
    """User-submitted support request."""

    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        IN_PROGRESS = "in_progress", _("In Progress")
        RESOLVED = "resolved", _("Resolved")
        CLOSED = "closed", _("Closed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets"
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ticket #{self.id} – {self.subject} [{self.status}]"
