from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import CustomUser


class ProductAccessTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        category = Category.objects.create(name="Категория")
        self.owner = CustomUser.objects.create_user(
            email="owner@mail.ru", username="owner", password="TestPass123!"
        )
        self.product = Product.objects.create(
            name="Товар",
            category=category,
            description="Описание",
            price=100,
            owner=self.owner,
            is_published=Product.Status.PUBLISHED,
        )

    def test_product_list_is_public(self) -> None:
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, response.context["products"])

    def test_unpublished_product_not_in_public_list(self) -> None:
        self.product.is_published = Product.Status.UNPUBLISHED
        self.product.save()
        response = self.client.get(reverse("catalog:index"))
        self.assertNotIn(self.product, response.context["products"])

    def test_product_detail_requires_login(self) -> None:
        url = reverse("catalog:product_detail", args=[self.product.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_product_create_requires_login(self) -> None:
        url = reverse("catalog:product_create")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_product_update_requires_login(self) -> None:
        url = reverse("catalog:product_update", args=[self.product.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_product_delete_requires_login(self) -> None:
        url = reverse("catalog:product_delete", args=[self.product.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('users:login')}?next={url}")

    def test_product_create_assigns_owner(self) -> None:
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("catalog:product_create"),
            {
                "name": "Новый товар",
                "category": self.product.category.pk,
                "price": "200",
            },
        )
        self.assertEqual(response.status_code, 302)
        product = Product.objects.get(name="Новый товар")
        self.assertEqual(product.owner, self.owner)

    def test_owner_can_update_product(self) -> None:
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("catalog:product_update", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_owner_can_delete_product(self) -> None:
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("catalog:product_delete", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_update_product(self) -> None:
        stranger = CustomUser.objects.create_user(
            email="stranger@mail.ru", username="stranger", password="TestPass123!"
        )
        self.client.force_login(stranger)
        response = self.client.get(
            reverse("catalog:product_update", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_delete_product(self) -> None:
        stranger = CustomUser.objects.create_user(
            email="stranger2@mail.ru", username="stranger2", password="TestPass123!"
        )
        self.client.force_login(stranger)
        response = self.client.get(
            reverse("catalog:product_delete", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_detail_buttons_hidden_for_non_owner(self) -> None:
        stranger = CustomUser.objects.create_user(
            email="stranger3@mail.ru", username="stranger3", password="TestPass123!"
        )
        url = reverse("catalog:product_detail", args=[self.product.pk])
        self.client.force_login(self.owner)
        self.client.get(url)
        self.client.logout()
        self.client.force_login(stranger)
        response = self.client.get(url)
        self.assertNotContains(response, "Редактировать")
        self.assertNotContains(response, "Удалить")

    def test_owner_sees_edit_button(self) -> None:
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse("catalog:product_detail", args=[self.product.pk])
        )
        self.assertContains(response, "Редактировать")
        self.assertContains(response, "Удалить")


class ModeratorTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        category = Category.objects.create(name="Категория")
        self.owner = CustomUser.objects.create_user(
            email="owner@mail.ru", username="owner", password="TestPass123!"
        )
        self.product = Product.objects.create(
            name="Товар",
            category=category,
            description="Описание",
            price=100,
            owner=self.owner,
            is_published=Product.Status.PUBLISHED,
        )

        content_type = ContentType.objects.get_for_model(Product)
        permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=["can_unpublish_product", "delete_product"],
        )
        group = Group.objects.create(name="Модератор продуктов")
        group.permissions.set(permissions)

        self.moderator = CustomUser.objects.create_user(
            email="moder@mail.ru", username="moder", password="TestPass123!"
        )
        self.moderator.groups.add(group)

    def test_moderator_can_delete_product(self) -> None:
        self.client.force_login(self.moderator)
        response = self.client.get(
            reverse("catalog:product_delete", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_moderator_can_update_product(self) -> None:
        self.client.force_login(self.moderator)
        response = self.client.get(
            reverse("catalog:product_update", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_moderator_can_unpublish_product(self) -> None:
        self.client.force_login(self.moderator)
        response = self.client.post(
            reverse("catalog:product_unpublish", args=[self.product.pk])
        )
        self.assertRedirects(
            response,
            reverse("catalog:product_detail", args=[self.product.pk]),
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.is_published, Product.Status.UNPUBLISHED)

    def test_ordinary_user_cannot_unpublish_product(self) -> None:
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("catalog:product_unpublish", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_unpublish_product(self) -> None:
        response = self.client.post(
            reverse("catalog:product_unpublish", args=[self.product.pk])
        )
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next="
            f"{reverse('catalog:product_unpublish', args=[self.product.pk])}",
        )


class CategoryAndCacheTests(TestCase):
    def setUp(self) -> None:
        cache.clear()
        self.category = Category.objects.create(name="Категория")
        self.other_category = Category.objects.create(name="Другая")
        self.user = CustomUser.objects.create_user(
            email="user@mail.ru", username="user", password="TestPass123!"
        )
        self.product = Product.objects.create(
            name="Товар",
            category=self.category,
            description="Описание",
            price=100,
            owner=self.user,
            is_published=Product.Status.PUBLISHED,
        )
        self.other = Product.objects.create(
            name="Другой",
            category=self.other_category,
            description="Описание",
            price=200,
            owner=self.user,
            is_published=Product.Status.PUBLISHED,
        )

    def test_category_products_page_available(self) -> None:
        url = reverse("catalog:category_products", args=[self.category.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product, response.context["products"])
        self.assertNotIn(self.other, response.context["products"])

    def test_category_products_cached_by_category_key(self) -> None:
        cache.clear()
        url = reverse("catalog:category_products", args=[self.category.pk])
        self.client.get(url)
        cached = cache.get(f"category_{self.category.pk}")
        self.assertIsNotNone(cached)
        self.assertIn(self.product, cached)
        self.assertNotIn(self.other, cached)

    def test_category_cache_invalidated_on_save(self) -> None:
        cache.clear()
        url = reverse("catalog:category_products", args=[self.category.pk])
        self.client.get(url)
        self.assertIsNotNone(cache.get(f"category_{self.category.pk}"))
        self.product.is_published = Product.Status.UNPUBLISHED
        self.product.save()
        self.assertIsNone(cache.get(f"category_{self.category.pk}"))

    def test_category_products_page_skips_unpublished(self) -> None:
        self.product.is_published = Product.Status.UNPUBLISHED
        self.product.save()
        url = reverse("catalog:category_products", args=[self.category.pk])
        response = self.client.get(url)
        self.assertNotIn(self.product, response.context["products"])

    def test_products_list_is_cached(self) -> None:
        cache.clear()
        self.client.get(reverse("catalog:index"))
        cached = cache.get("products_list")
        self.assertIsNotNone(cached)
        self.assertIn(self.product, cached)

    def test_new_published_product_appears_on_main(self) -> None:
        cache.clear()
        self.client.get(reverse("catalog:index"))
        new_product = Product.objects.create(
            name="Свежий товар",
            category=self.category,
            description="Описание",
            price=300,
            owner=self.user,
            is_published=Product.Status.PUBLISHED,
        )
        response = self.client.get(reverse("catalog:index"))
        self.assertIn(new_product, response.context["products"])

    def test_products_list_cache_invalidated_on_save(self) -> None:
        cache.clear()
        self.client.get(reverse("catalog:index"))
        self.assertIsNotNone(cache.get("products_list"))
        self.product.is_published = Product.Status.UNPUBLISHED
        self.product.save()
        self.assertIsNone(cache.get("products_list"))