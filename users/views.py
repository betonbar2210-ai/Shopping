from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from users.forms import UserRegistration


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