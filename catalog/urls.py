from django.urls import path
from catalog.apps import CatalogConfig
from catalog.views import index, contacts, product_detail

app_name = CatalogConfig.name

urlpatterns = [
    path("", index, name="index"),
    path("contacts/", contacts, name="contacts"),
    path("products/<int:pk>/", product_detail, name="product_detail")
]
