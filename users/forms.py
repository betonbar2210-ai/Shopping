from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser


class UserRegistration(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "password1",
            "password2",
            "avatar",
            "phone",
            "country",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Email"}
        )
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Username"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторите пароль"}
        )
        self.fields["avatar"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Аватар"}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Телефон"}
        )
        self.fields["country"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Страна"}
        )
