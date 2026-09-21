from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import CustomUser


class ProductAccessTests(TestCase):
    def setUp(self) -> None:
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


class ModeratorTests(TestCase):
    def setUp(self) -> None:
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