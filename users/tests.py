from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class UserRegistrationTests(TestCase):
    def setUp(self) -> None:
        self.url = reverse("users:register")
        self.data = {
            "email": "test@mail.ru",
            "username": "testuser",
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }

    def test_registration_creates_user_and_redirects(self) -> None:
        response = self.client.post(self.url, self.data)
        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(
            CustomUser.objects.filter(email=self.data["email"]).exists()
        )

    def test_registration_sends_welcome_email(self) -> None:
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.data["email"], mail.outbox[0].to)

    def test_registration_page_available(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class UserLoginTests(TestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(
            email="login@mail.ru",
            username="loginuser",
            password="TestPass123!",
        )

    def test_login_by_email(self) -> None:
        response = self.client.post(
            reverse("users:login"),
            {"username": "login@mail.ru", "password": "TestPass123!"},
        )
        self.assertEqual(response.status_code, 302)

        user = get_user_model()
        authenticated = user.objects.get(email="login@mail.ru")
        self.assertTrue(
            self.client.login(
                username=authenticated.email, password="TestPass123!"
            )
        )

    def test_profile_page_requires_login(self) -> None:
        response = self.client.get(reverse("users:profile"))
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('users:profile')}",
        )

    def test_profile_update(self) -> None:
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:profile"),
            {
                "email": "login@mail.ru",
                "username": "newusername",
                "phone": "+79001234567",
                "country": "RU",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")
        self.assertEqual(str(self.user.phone), "+79001234567")