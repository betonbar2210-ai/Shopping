from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import BlogPost
from django.urls import reverse_lazy


class BlogListView(ListView):
    model = BlogPost
    template_name = "blogs/blog_list.html"
    context_object_name = "blogs"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        object.views_count += 1
        object.save()
        return object


class BlogCreateView(CreateView):
    model = BlogPost
    fields = ["title", "content", "preview_image"]
    template_name = "blogs/blog_form.html"
    success_url = reverse_lazy("blogs:blog_list")


class BlogUpdateView(UpdateView):
    model = BlogPost
    fields = ["title", "content", "preview_image"]
    template_name = "blogs/blog_form.html"
    success_url = reverse_lazy("blogs:blog_list")

    def get_success_url(self):
        return reverse_lazy("blogs:blog_detail", kwargs={"pk": self.object.pk})


class BlogDeleteView(DeleteView):
    model = BlogPost
    template_name = "blogs/blog_delete.html"
    context_object_name = "blog"
    success_url = reverse_lazy("blogs:blog_list")
