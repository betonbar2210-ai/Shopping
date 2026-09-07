from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import BlogPost
from django.urls import reverse_lazy


class BlogListView(ListView):
    model = BlogPost
    template_name = "blogs/blog_list.html"
    context_object_name = "blogs"


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "blogs/blog_detail.html"
    context_object_name = "blog"


class BlogCreateView(CreateView):
    model = BlogPost
    fields = ['title', 'content']
    template_name = "blogs/blog_create.html"
    success_url = reverse_lazy('blogs:blog_list')


class BlogUpdateView(UpdateView):
    model = BlogPost
    fields = ['title', 'content']
    template_name = "blogs/blog_update.html"
    success_url = reverse_lazy('blogs:blog_list')


class BlogDeleteView(DeleteView):
    model = BlogPost
    template_name = "blogs/blog_delete.html"
    success_url = reverse_lazy('blogs:blog_list')
