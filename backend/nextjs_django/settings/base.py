"""
For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from .env_vars import env, BASE_DIR
# from celery.schedules import crontab

from .allauth import *
from .compressor import *

# from .channels import *
from .crispy_form import *
from .database import *
from .email import *
from .google import *
from .graphql import *

# from .graphql import *
from .rest import *
from .stripe import *
from .timezone_language import *


# New for Django 3.2
# https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# ALLOWED_HOSTS
ALLOWED_HOSTS = eval(env("ALLOWED_HOSTS"))

# Sitemaps
# Need to update database table: django_site manual from example.com to domain name, which match record ID=1
SITE_ID = 1
SITE_NAME = "nextjs_django"
SITE_URL = "https://nextjs_django.com/"

# Define Local Server MEDIA_ROOT for User-uploaded files like profile pics need to be served
STATIC_URL = "static/"  # Local
MEDIA_URL = "media/"  # Local

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")

# Use PBKDF2 algorithm with a SHA256 hash
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
# https://docs.djangoproject.com/en/3.0/topics/auth/passwords/#password-validation
# AUTH_PASSWORD_VALIDATORS = [
#     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
#     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
# ]

# Use Django templates using the new Django 1.8 TEMPLATES settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR.joinpath("templates"),
            # insert more TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                # django-allauth needs this from django
                "django.template.context_processors.request",
                # global settings for templates. Need update nextjs_django to project folder name
                "nextjs_django.context_processors.global_settings",
            ],
        },
    },
]

# Application definition
INSTALLED_APPS = (
    "daphne",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_recaptcha",
    # 'autotranslate',
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "corsheaders",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    # "api",

    'graphene_django',
    'book_graphql',

    # 'chat',
    "compressor",
    "crispy_forms",
    "crispy_bootstrap5",
    "dbbackup",
    
    # Combined-monorepo apps (mirror the former Next.js Prisma schema)
    "accounts",
    # "blog",
    # "billing",
    # "core",
    "profiles",
    "tenants",
)

# Custom user model (email-based login) — see accounts/models.py
AUTH_USER_MODEL = "accounts.User"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

MIDDLEWARE = (
    # CORS must come before CommonMiddleware so it can attach headers
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # 'whitenoise.middleware.WhiteNoiseMiddleware',
    "allauth.account.middleware.AccountMiddleware",
)

ROOT_URLCONF = "nextjs_django.urls"
ASGI_APPLICATION = "nextjs_django.asgi.application"


# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
