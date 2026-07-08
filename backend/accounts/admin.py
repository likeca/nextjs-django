from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    EmailChangeRequest,
    Permission,
    Role,
    RolePermission,
    TwoFactor,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "name", "is_admin", "role", "is_active", "created_at")
    list_filter = ("is_admin", "is_active", "is_staff", "role")
    search_fields = ("email", "name")
    readonly_fields = ("id", "created_at", "updated_at", "last_login")
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Profile", {"fields": ("name", "phone", "image", "email_verified")}),
        ("Roles & permissions", {"fields": ("is_admin", "role", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Billing", {"fields": ("stripe_customer_id",)}),
        ("Security", {"fields": ("two_factor_enabled", "is_active")}),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2"),
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_system", "created_at")
    search_fields = ("name",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "resource", "action")
    list_filter = ("resource", "action")
    search_fields = ("name", "resource", "action")


admin.site.register(RolePermission)
admin.site.register(EmailChangeRequest)
admin.site.register(TwoFactor)
