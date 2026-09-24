from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the least-privilege dashboard role groups. Assign is_staff separately to dashboard users."

    def handle(self, *args, **options):
        app_permissions = Permission.objects.filter(content_type__app_label__in=["core", "portfolio", "contact"])
        manager_permissions = app_permissions
        editor_permissions = app_permissions.filter(codename__regex=r"^(add|change|delete|view)_").exclude(
            content_type__app_label="core"
        ).exclude(codename="publish_project").exclude(codename="manage_profile").exclude(
            content_type__app_label="contact"
        )
        viewer_permissions = app_permissions.filter(codename__startswith="view_").exclude(content_type__app_label="contact")

        groups = {
            "Content Manager": manager_permissions,
            "Editor": editor_permissions,
            "Viewer": viewer_permissions,
        }
        for name, permissions in groups.items():
            group, created = Group.objects.get_or_create(name=name)
            group.permissions.set(permissions)
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'} {name}"))

        self.stdout.write(
            "Super Admin is represented by Django's is_superuser flag. "
            "Users must also be marked is_staff before they can enter the custom dashboard."
        )
