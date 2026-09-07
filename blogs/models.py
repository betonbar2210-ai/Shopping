from django.db import models


class BlogPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="заголовок", help_text="заголовок статьи")
    content = models.TextField(blank=True, null=True, verbose_name="текст", help_text="текст статьи")
    preview_image = models.ImageField(upload_to='previews/', blank=True, null=True, verbose_name="изображение", help_text="изображение статьи")
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField( default=False, help_text='Признак публикации')
    views_count = models.PositiveIntegerField(default=0, help_text='Количество просмотров')

    def __str__(self):
        return self.title

