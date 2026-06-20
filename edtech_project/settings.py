"""
EdTech Platform – Django Settings
Split into base / dev / prod via django-environ.
"""
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

# ─── Security ───────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-in-production")
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Security headers (enable in production)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = "DENY"

# ─── Applications ────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.courses",
    "apps.tests",
    "apps.ai_doubt",
    "apps.analytics",
    "apps.achievements",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── Middleware ──────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "edtech_project.urls"
WSGI_APPLICATION = "edtech_project.wsgi.application"

# ─── Templates ───────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.courses.context_processors.categories_processor",
            ],
        },
    },
]

# ─── Database ────────────────────────────────────────────────
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3")
}

# ─── Auth ────────────────────────────────────────────────────
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── Internationalisation ────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ─── Static & Media ─────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Crispy Forms ────────────────────────────────────────────
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ─── Email ───────────────────────────────────────────────────
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER", default="noreply@edtech.com")

# ─── Third-party API Keys ────────────────────────────────────
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")
RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")

# ─── Support Contacts ────────────────────────────────────────
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="9584889727")
SUPPORT_EMAIL = env("SUPPORT_EMAIL", default="adityabijore6024@gmail.com")

# ─── Session ─────────────────────────────────────────────────
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True

# ─── CORS ────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = DEBUG







# Setting for Railway 
# """
# EdTech Platform – Django Settings (Optimized for Railway.app)
# """
# import os
# from pathlib import Path
# import environ

# BASE_DIR = Path(__file__).resolve().parent.parent

# env = environ.Env(DEBUG=(bool, False))

# # FIXED 1: Fail-safe environment reading (Railway dashboard variables won't crash this)
# env_file = BASE_DIR / ".env"
# if env_file.exists():
#     environ.Env.read_env(env_file)

# # ─── Security ───────────────────────────────────────────────
# SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-in-production")
# DEBUG = env("DEBUG", default=True)

# # FIXED 2: Automatically allows Railway's dynamic subdomains
# ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", ".railway.app"])

# # FIXED 3: Crucial for Django 4.0+ to allow POST requests (Login/Ask Doubt) on Railway
# CSRF_TRUSTED_ORIGINS = env.list(
#     "CSRF_TRUSTED_ORIGINS", 
#     default=["https://*.railway.app", "http://localhost:8000", "http://127.0.0.1:8000"]
# )

# # Security headers (Enabled in production)
# if not DEBUG:
#     # FIXED 4: Tells Django it's sitting behind Railway's secure SSL Proxy
#     SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    
#     SECURE_BROWSER_XSS_FILTER = True
#     SECURE_CONTENT_TYPE_NOSNIFF = True
#     SECURE_HSTS_SECONDS = 31536000
#     SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#     SECURE_SSL_REDIRECT = True
#     SESSION_COOKIE_SECURE = True
#     CSRF_COOKIE_SECURE = True
#     X_FRAME_OPTIONS = "DENY"

# # ─── Applications ────────────────────────────────────────────
# DJANGO_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "django.contrib.humanize",
# ]

# THIRD_PARTY_APPS = [
#     "crispy_forms",
#     "crispy_bootstrap5",
#     "widget_tweaks",
#     "corsheaders",
# ]

# LOCAL_APPS = [
#     "apps.accounts",
#     "apps.courses",
#     "apps.tests",
#     "apps.ai_doubt",
#     "apps.analytics",
#     "apps.achievements",
# ]

# INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# # ─── Middleware ──────────────────────────────────────────────
# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "whitenoise.middleware.WhiteNoiseMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "edtech_project.urls"
# WSGI_APPLICATION = "edtech_project.wsgi.application"

# # ─── Templates ───────────────────────────────────────────────
# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#                 "apps.courses.context_processors.categories_processor",
#             ],
#         },
#     },
# ]

# # ─── Database ────────────────────────────────────────────────
# # Works locally with SQLite. When you attach Railway Postgres, it auto-switches!
# DATABASES = {
#     "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3")
# }

# # ─── Auth ────────────────────────────────────────────────────
# AUTH_USER_MODEL = "accounts.User"
# LOGIN_URL = "/auth/login/"
# LOGIN_REDIRECT_URL = "/dashboard/"
# LOGOUT_REDIRECT_URL = "/"

# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# # ─── Internationalisation ────────────────────────────────────
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "Asia/Kolkata"
# USE_I18N = True
# USE_TZ = True

# # ─── Static & Media ─────────────────────────────────────────
# STATIC_URL = "/static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_DIRS = [BASE_DIR / "static"]

# # FIXED 5: Changed to standard storage. Prevents the deployment from failing 
# # just because a single .png file referenced in your CSS went missing.
# STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # ─── Crispy Forms ────────────────────────────────────────────
# CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
# CRISPY_TEMPLATE_PACK = "bootstrap5"

# # ─── Email ───────────────────────────────────────────────────
# EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
# EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
# EMAIL_PORT = env.int("EMAIL_PORT", default=587)
# EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
# EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
# EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
# DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER", default="noreply@edtech.com")

# # ─── Third-party API Keys ────────────────────────────────────
# GEMINI_API_KEY = env("GEMINI_API_KEY", default=None)
# RAZORPAY_KEY_ID = env("RAZORPAY_KEY_ID", default="")
# RAZORPAY_KEY_SECRET = env("RAZORPAY_KEY_SECRET", default="")

# # ─── Support Contacts ────────────────────────────────────────
# WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="9584889727")
# SUPPORT_EMAIL = env("SUPPORT_EMAIL", default="adityabijore6024@gmail.com")

# # ─── Session ─────────────────────────────────────────────────
# SESSION_COOKIE_AGE = 86400 * 30  # 30 days
# SESSION_SAVE_EVERY_REQUEST = True

# # ─── CORS ────────────────────────────────────────────────────
# CORS_ALLOW_ALL_ORIGINS = DEBUG


