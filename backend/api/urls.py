from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views import (
    DashboardStatsView,
    EmailChangeConfirmView,
    EmailChangeRequestView,
    EmailOTPSendView,
    EmailOTPVerifyView,
    LoginView,
    PermissionViewSet,
    RoleViewSet,
    TwoFactorDisableView,
    TwoFactorEnableView,
    TwoFactorLoginVerifyView,
    TwoFactorVerifyView,
    UserViewSet,
)
# billing app disabled — see INSTALLED_APPS
# from billing.views import (
#     CancelSubscriptionView,
#     CreateBillingPortalSessionView,
#     CreateCheckoutSessionView,
#     PaymentViewSet,
#     PlanViewSet,
#     ResumeSubscriptionView,
#     SubscriptionViewSet,
#     VerifyCheckoutSessionView,
# )
# from billing.webhooks import stripe_webhook
# blog app disabled — see INSTALLED_APPS
# from blog.views import BlogViewSet
# core app disabled — see INSTALLED_APPS
# from core.views import (
#     ApiKeyViewSet,
#     ContactSubmissionViewSet,
#     OrganizationViewSet,
#     SettingViewSet,
# )

from . import views

app_name = "api"

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")
router.register("permissions", PermissionViewSet, basename="permission")
# blog routes disabled
# router.register("blogs", BlogViewSet, basename="blog")
# core routes disabled
# router.register("settings", SettingViewSet, basename="setting")
# router.register("contact", ContactSubmissionViewSet, basename="contact")
# billing routes disabled
# router.register("billing/plans", PlanViewSet, basename="plan")
# router.register("billing/subscriptions", SubscriptionViewSet, basename="subscription")
# router.register("billing/payments", PaymentViewSet, basename="payment")
# router.register("api-keys", ApiKeyViewSet, basename="apikey")
# router.register("organizations", OrganizationViewSet, basename="organization")

urlpatterns = [
    # ─── Auth (dj-rest-auth + JWT) ───────────────────────────────────────────
    # Custom login overrides dj-rest-auth's to gate 2FA-enabled users (must come first).
    path("auth/login/", LoginView.as_view(), name="login"),
    path(
        "auth/2fa/login-verify/",
        TwoFactorLoginVerifyView.as_view(),
        name="2fa_login_verify",
    ),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("auth/google/", views.GoogleSignin.as_view(), name="google_login"),
    # Email OTP (replaces better-auth emailOTP plugin)
    path("auth/otp/send/", EmailOTPSendView.as_view(), name="otp_send"),
    path("auth/otp/verify/", EmailOTPVerifyView.as_view(), name="otp_verify"),
    # TOTP 2FA (replaces better-auth twoFactor plugin)
    path("auth/2fa/enable/", TwoFactorEnableView.as_view(), name="2fa_enable"),
    path("auth/2fa/verify/", TwoFactorVerifyView.as_view(), name="2fa_verify"),
    path("auth/2fa/disable/", TwoFactorDisableView.as_view(), name="2fa_disable"),
    path(
        "user/email-change/",
        EmailChangeRequestView.as_view(),
        name="email_change_request",
    ),
    path(
        "user/email-change/confirm/",
        EmailChangeConfirmView.as_view(),
        name="email_change_confirm",
    ),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard_stats"),
    # ─── Stripe (billing app disabled) ───────────────────────────────────────
    # path("billing/checkout/", CreateCheckoutSessionView.as_view(), name="billing_checkout"),
    # path("billing/portal/", CreateBillingPortalSessionView.as_view(), name="billing_portal"),
    # path("billing/cancel/", CancelSubscriptionView.as_view(), name="billing_cancel"),
    # path("billing/resume/", ResumeSubscriptionView.as_view(), name="billing_resume"),
    # path("billing/verify-session/", VerifyCheckoutSessionView.as_view(), name="billing_verify"),
    # path("billing/webhook/", stripe_webhook, name="billing_webhook"),
    # ─── Resource API (replaces the Next.js server actions) ──────────────────
    path("groups/", views.GroupView.as_view()),
    path("", include(router.urls)),
]
