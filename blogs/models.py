from django.db import models


class BlogPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="заголовок")
    content = models.TextField(blank=True, null=True, verbose_name="текст")
    preview_image = models.ImageField(
        upload_to="previews/", blank=True, null=True, verbose_name="изображение"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True, help_text="Признак публикации")
    views_count = models.PositiveIntegerField(
        default=0, help_text="Количество просмотров"
    )

    class Meta:
            ordering = ("title")
            verbose_name = "статья"
            verbose_name_plural = "статьи"

    def __str__(self):
        return self.title
