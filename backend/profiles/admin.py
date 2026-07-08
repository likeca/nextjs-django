from django.contrib import admin

from profiles.models import Profile

# NOTE: the custom user (accounts.User) is registered in accounts/admin.py.
# Profile is registered standalone here to avoid clobbering that registration.


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "province", "country", "email_verified")
    search_fields = ("user__email", "user__name", "city")
    list_filter = ("email_verified", "province", "country")
