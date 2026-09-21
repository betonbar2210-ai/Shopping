from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.cache import cache
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView

from .cache_keys import PRODUCTS_CACHE_KEY
from .forms import ProductForm
from .models import Category, Product
from .services import get_products_by_category


class ContactsView(TemplateView):
    template_name = "catalog/contacts.html"


class ProductListView(ListView):
    model = Product
    template_name = "catalog/index.html"
    context_object_name = "products"

    def get_queryset(self):
        products = cache.get(PRODUCTS_CACHE_KEY)
        if products is None:
            products = list(
                Product.objects.filter(is_published=Product.Status.PUBLISHED)
            )
            cache.set(PRODUCTS_CACHE_KEY, products, 60)
        return products


@method_decorator(cache_page(60), name="dispatch")
@method_decorator(vary_on_cookie, name="dispatch")
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        Product.objects.filter(pk=self.object.pk).update(
            views_count=F("views_count") + 1
        )
        self.object.views_count += 1
        return self.object


class CategoryProductsView(ListView):
    model = Product
    template_name = "catalog/category_products.html"
    context_object_name = "products"

    def get_queryset(self):
        category = get_object_or_404(Category, pk=self.kwargs["pk"])
        return get_products_by_category(category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = get_object_or_404(Category, pk=self.kwargs["pk"])
        return context


class OwnerOrModeratorMixin(UserPassesTestMixin):
    def test_func(self):
        product = self.get_object()
        return product.owner == self.request.user or self.request.user.has_perm(
            "catalog.delete_product"
        )


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:index")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(OwnerOrModeratorMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:index")

    def get_success_url(self):
        return reverse_lazy("catalog:product_detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(OwnerOrModeratorMixin, DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:index")


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "catalog.can_unpublish_product"

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_published = Product.Status.UNPUBLISHED
        product.save()
        return HttpResponseRedirect(
            reverse("catalog:product_detail", kwargs={"pk": product.pk})
        )