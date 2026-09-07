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
    name = models.CharField(
        max_length=200, verbose_name="товар", help_text="название товара"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="категория",
        related_name="products",
    )
    description = models.TextField(blank=True, null=True, help_text="описание товара")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="цена", help_text="цена товара"
    )
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, help_text="изображение товара"
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="дата обновления")
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("name",)
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return self.name
