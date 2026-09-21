from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from catalog.models import Product


class Command(BaseCommand):
    help = "Create the 'Модератор продуктов' group with product permissions"

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(Product)

        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=["can_unpublish_product", "delete_product"],
        )

        group, created = Group.objects.get_or_create(name="Модератор продуктов")
        group.permissions.set(permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    "Group 'Модератор продуктов' created with permissions: "
                    + ", ".join(permissions.values_list("codename", flat=True))
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Group 'Модератор продуктов' already exists, permissions updated: "
                    + ", ".join(permissions.values_list("codename", flat=True))
                )
            )