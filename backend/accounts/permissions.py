"""RBAC permission helpers mirroring the frontend's requirePermission(resource, action)."""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import RolePermission


def user_has_permission(user, resource: str, action: str) -> bool:
    """Return True if the user may perform (resource, action).

    Mirrors the former Next.js lib/permissions.hasPermission semantics:
      1. Django superusers bypass everything.
      2. A "Super Admin" (is_admin + role name "Super Admin") bypasses everything.
      3. Otherwise the user must be an admin (admin-area gating) AND their role
         must carry the explicit (resource, action) permission.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if getattr(user, "is_admin", False) and user.role_id and user.role.name == "Super Admin":
        return True
    # Admin-area gating: non-admins can never pass an RBAC check.
    if not getattr(user, "is_admin", False):
        return False
    if not user.role_id:
        return False
    return RolePermission.objects.filter(
        role_id=user.role_id,
        permission__resource=resource,
        permission__action=action,
    ).exists()


def user_permission_summary(user) -> dict:
    """Effective permission summary for the current user (for the frontend)."""
    if not user or not user.is_authenticated:
        return {"isAuthenticated": False, "isAdmin": False, "isSuperuser": False,
                "roleName": None, "permissions": []}
    perms = []
    if user.role_id:
        perms = [
            {"resource": r, "action": a}
            for r, a in RolePermission.objects.filter(role_id=user.role_id).values_list(
                "permission__resource", "permission__action"
            )
        ]
    return {
        "isAuthenticated": True,
        "isAdmin": bool(getattr(user, "is_admin", False)),
        "isSuperuser": bool(user.is_superuser),
        "roleName": user.role.name if user.role_id else None,
        "permissions": perms,
    }


def can_access_user(editor, target_user_id: str) -> bool:
    """Mirrors lib/permissions.canAccessUser (self / Super Admin / user.update_any)."""
    if not editor or not editor.is_authenticated:
        return False
    if str(editor.id) == str(target_user_id):
        return True
    if editor.is_superuser:
        return True
    if editor.is_admin and editor.role_id and editor.role.name == "Super Admin":
        return True
    if not editor.role_id:
        return False
    return RolePermission.objects.filter(
        role_id=editor.role_id,
        permission__resource="user",
        permission__action="update_any",
    ).exists()


class HasResourcePermission(BasePermission):
    """
    Generic DRF permission that maps the view action to an RBAC (resource, action).

    Set ``rbac_resource`` on the view. The DRF action is mapped to a CRUD verb:
    list/retrieve -> read, create -> create, update/partial_update -> update,
    destroy -> delete.
    """

    action_to_verb = {
        "list": "read",
        "retrieve": "read",
        "create": "create",
        "update": "update",
        "partial_update": "update",
        "destroy": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        resource = getattr(view, "rbac_resource", None)
        if resource is None:
            return True  # no RBAC declared -> just require authentication

        verb = self.action_to_verb.get(getattr(view, "action", ""), None)
        if verb is None:
            # Fall back to read for safe methods, deny otherwise.
            verb = "read" if request.method in SAFE_METHODS else "update"

        return user_has_permission(user, resource, verb)


class IsAdminUser(BasePermission):
    """App-level admin (accounts.User.is_admin) or Django superuser."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "is_admin", False) or user.is_superuser)
        )
