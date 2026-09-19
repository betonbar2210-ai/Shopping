from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import CustomUser


class ProductAccessTests(TestCase):
    def setUp(self) -> None:
        category = Category.objects.create(name="Категория")
        self.product = Product.objects.create(
            name="Товар",
            category=category,
            description="Описание",
            price=100,
        )

    def test_product_list_is_public(self) -> None:
        response = self.client.get(reverse("catalog:index"))
        self.assertEqual(response.status_code, 200)

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

    def test_authenticated_user_can_open_product_detail(self) -> None:
        user = CustomUser.objects.create_user(
            email="client@mail.ru", username="client", password="TestPass123!"
        )
        self.client.force_login(user)
        response = self.client.get(
            reverse("catalog:product_detail", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, 200)