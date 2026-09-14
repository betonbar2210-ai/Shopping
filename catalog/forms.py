from django import forms
from django.core.exceptions import ValidationError

from catalog.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "price", "image", "description"]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Название"}
        )

        self.fields["category"].widget.attrs.update({"class": "form-control"})

        self.fields["price"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Цена"}
        )

        self.fields["image"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Изображение"}
        )

        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Описание"}
        )

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

    def clean(self):
        stop_text = [
            "казино",
            "криптовалюта",
            "крипта",
            "дешево",
            "бесплатно",
            "обман",
            "полиция",
            "радар",
            "биржа",
        ]
        for field_name, value in self.cleaned_data.items():
            if not isinstance(value, str):
                continue
            for stop in stop_text:
                if stop in value.lower():
                    raise ValidationError({field_name: f"{stop} - запрещенное слово"})
        return self.cleaned_data

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Product.objects.filter(name=name).exists():
            raise ValidationError("Товар с таким именем существует")
        return name
