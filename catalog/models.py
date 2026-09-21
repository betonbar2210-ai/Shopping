from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="категория", help_text="название категории"
    )
    description = models.TextField(
        blank=True, null=True, help_text="описание категории"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        UNPUBLISHED = "unpublished", "Не опубликован"
        PUBLISHED = "published", "Опубликован"

    name = models.CharField(max_length=200, verbose_name="товар")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="категория",
        related_name="products",
    )
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="цена")
    image = models.ImageField(
        upload_to="products/", verbose_name="изображение", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UNPUBLISHED,
        verbose_name="статус публикации",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="владелец",
        related_name="products",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "товар"
        verbose_name_plural = "товары"
        permissions = [
            ("can_unpublish_product", "Может отменять публикацию продукта"),
        ]

    def __str__(self):
        return self.name
