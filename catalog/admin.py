from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "category",
        "owner",
        "is_published",
    )
    list_filter = ("category", "is_published")
    search_fields = (
        "name",
        "description",
    )

    actions = ["publish_products", "unpublish_products"]

    @admin.action(description="Опубликовать выбранные товары")
    def publish_products(self, request, queryset):
        queryset.update(is_published="published")

    @admin.action(description="Снять с публикации выбранные товары")
    def unpublish_products(self, request, queryset):
        queryset.update(is_published="unpublished")
