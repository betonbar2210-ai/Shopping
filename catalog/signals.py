from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from catalog.cache_keys import PRODUCTS_CACHE_KEY, category_cache_key
from catalog.models import Product


def _delete_cache_by_category(category_id):
    if category_id is not None:
        cache.delete(category_cache_key(category_id))


@receiver(pre_save, sender=Product)
def remember_old_category(sender, instance, **kwargs):
    if kwargs.get("update_fields"):
        return
    if instance.pk:
        try:
            instance._old_category_id = (
                Product.objects.only("category_id").get(pk=instance.pk).category_id
            )
        except Product.DoesNotExist:
            instance._old_category_id = None
    else:
        instance._old_category_id = None


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_products_cache(sender, instance, **kwargs):
    if kwargs.get("update_fields") and set(kwargs["update_fields"]) <= {"views_count"}:
        return
    cache.delete(PRODUCTS_CACHE_KEY)
    _delete_cache_by_category(instance.category_id)
    old = getattr(instance, "_old_category_id", None)
    if old is not None and old != instance.category_id:
        _delete_cache_by_category(old)