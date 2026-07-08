"""Seed default RBAC permissions + roles and (optionally) an admin user.

Replaces the former Next.js scripts: create-admin.ts, create-blog-permissions.ts.

Usage:
    python manage.py seed_rbac
    python manage.py seed_rbac --admin-email admin@example.com --admin-password secret123
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Permission, Role, RolePermission, User

RESOURCES = ["user", "role", "permission", "blog", "settings", "contact"]
ACTIONS = ["create", "read", "update", "delete"]


class Command(BaseCommand):
    help = "Seed default RBAC permissions, roles, and an optional admin user."

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default=None)
        parser.add_argument("--admin-password", default=None)
        parser.add_argument("--admin-name", default="Administrator")

    @transaction.atomic
    def handle(self, *args, **options):
        # 1) Permissions: full CRUD matrix across resources.
        perms = {}
        for resource in RESOURCES:
            for action in ACTIONS:
                perm, _ = Permission.objects.get_or_create(
                    resource=resource,
                    action=action,
                    defaults={"name": f"{resource}.{action}"},
                )
                perms[(resource, action)] = perm
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(perms)} permissions."))

        # 2) Roles.
        admin_role, _ = Role.objects.get_or_create(
            name="Admin", defaults={"description": "Full access", "is_system": True}
        )
        editor_role, _ = Role.objects.get_or_create(
            name="Editor", defaults={"description": "Manage blog content", "is_system": True}
        )

        # Admin gets everything.
        RolePermission.objects.filter(role=admin_role).delete()
        RolePermission.objects.bulk_create(
            [RolePermission(role=admin_role, permission=p) for p in perms.values()]
        )
        # Editor gets blog CRUD + read settings.
        editor_perms = [perms[("blog", a)] for a in ACTIONS] + [perms[("settings", "read")]]
        RolePermission.objects.filter(role=editor_role).delete()
        RolePermission.objects.bulk_create(
            [RolePermission(role=editor_role, permission=p) for p in editor_perms]
        )
        self.stdout.write(self.style.SUCCESS("Ensured Admin and Editor roles."))

        # 3) Optional admin user.
        email = options["admin_email"]
        password = options["admin_password"]
        if email and password:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": options["admin_name"], 
                    "is_admin": True,
                    "is_staff": True,
                    "is_superuser": True,
                    "email_verified": True,
                },
            )
            user.role = admin_role
            user.set_password(password)
            user.is_admin = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{verb} admin user {email}."))
        else:
            self.stdout.write(
                "Skipped admin user (pass --admin-email and --admin-password to create one)."
            )
