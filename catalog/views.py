from django.shortcuts import render, get_object_or_404
from .models import Product


def contacts(request):
    return render(request, "catalog/contacts.html")


def index(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "catalog/index.html", context=context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {"product": product}
    return render(request, "catalog/product_detail.html", context=context)
