from django.urls import reverse_lazy
from .env_vars import env

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of django-allauth
    "django.contrib.auth.backends.ModelBackend",
    # django-allauth specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="info@django.com")
# "mandatory" | "optional" | "none". Default to optional so the API-driven
# frontend flow works without blocking on SMTP during development.
ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION", default="optional")

# Email-based auth to match the custom (username-less) accounts.User.
# django-allauth > 65.4.0, conflict with dj-rest-auth 7.0.1
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

ACCOUNT_FORMS = {
    "signup": "nextjs_django.forms.AllauthSignupForm",
    "login": "nextjs_django.forms.AllauthSigninForm",
}
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
LOGIN_REDIRECT_URL = reverse_lazy("profiles:show_self")  # Redirect after sign in
# LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = reverse_lazy("home")

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_AUTH_CLIENT_ID"),
            "secret": env("GOOGLE_AUTH_SECRET"),
            "key": env("GOOGLE_AUTH_KEY"),
        }
    }
}
