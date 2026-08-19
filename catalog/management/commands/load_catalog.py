from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Удаляем продукты и категории, загрузить фикстуры"

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write("Категории и продукты удалены")

        self.stdout.write("Загрузка фикстур")
        call_command("loaddata", "catalog/fixtures/catalog_data.json")

        self.stdout.write(self.style.SUCCESS("Каталог успешно перезагружен!"))
