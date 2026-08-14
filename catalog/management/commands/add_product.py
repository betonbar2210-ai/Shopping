from django.core.management.base import BaseCommand
from catalog.models import Product, Category


class Command(BaseCommand):
    help = "Add a new product"

    def handle(self, *args, **options):
        category, _ = Category.objects.get_or_create(
            name="Забор", description="Забор железобетонный"
        )
        products = [
            {
                "name": "ПО-2м",
                "description": "Забор 2500/3000 с фартуком",
                "price": "12800",
                "category": category,
            },
            {
                "name": "ПО-2",
                "description": "Забор 3000/3000 без фартука",
                "price": "12100",
                "category": category,
            },
        ]

        for prod in products:
            product, created = Product.objects.get_or_create(**prod)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"{product.name} created successfully")
                )
            else:
                self.stdout.write(self.style.SUCCESS(f"{product.name} already exists"))
