from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from users.forms import UserProfileForm, UserRegistration
from users.models import CustomUser


class RegisterView(CreateView):
    form_class = UserRegistration
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        send_mail(
            subject="Добро пожаловать в SkyproStore!",
            message=(
                "Вы успешно зарегистрировались в SkyproStore.\n"
                "Спасибо за регистрацию и приятных покупок!"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[form.cleaned_data["email"]],
        )
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    success_url = reverse_lazy("catalog:index")

    def get_object(self, queryset=None) -> CustomUser:
        return self.request.user
