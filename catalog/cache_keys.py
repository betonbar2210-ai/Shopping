CACHE_TTL_SECONDS = 60 * 15
PRODUCTS_CACHE_KEY = "products_list"


def category_cache_key(category_id):
    return f"category_{category_id}"