from django.core.cache import cache

from catalog.cache_keys import CACHE_TTL_SECONDS, category_cache_key
from catalog.models import Product


def get_products_by_category(category):
    """Возвращает опубликованные продукты категории.

    Данные кэшируются в Redis под ключом category_{id} на время CACHE_TTL_SECONDS.
    """
    cache_key = category_cache_key(category.pk)
    products = cache.get(cache_key)
    if products is None:
        products = list(
            Product.objects.filter(
                category=category,
                is_published=Product.Status.PUBLISHED,
            )
        )
        cache.set(cache_key, products, CACHE_TTL_SECONDS)
    return products