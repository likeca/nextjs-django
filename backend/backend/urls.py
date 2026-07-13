from django.urls import include, path
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from dj_rest_auth.views import PasswordResetConfirmView


from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from . import views, sitemaps

sitemaps = {
    "static": sitemaps.StaticViewSitemap,
}


urlpatterns = [
    # Remove Django admin login for security reason
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path(
        "api/auth/password-reset/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

    # Enable CSRF: https://docs.djangoproject.com/en/4.0/ref/csrf/#ajax
    path('graphql/', csrf_exempt(views.PrivateGraphQLView.as_view(graphiql=True))),
    # path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    # path("graphql/", GraphQLView.as_view(graphiql=True)),

    # path("openapi/", views.SwaggerPage.as_view(), name="openapi"),
    # path("chat/", include("chat.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("", views.HomePage.as_view(), name="home"),
    path("about/", views.AboutPage.as_view(), name="about"),
    path("accounts/", include("allauth.urls")),
    path("accounts/profile/", include("profiles.urls", namespace="profiles")),
    path("tenants/", include("tenants.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
)

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
