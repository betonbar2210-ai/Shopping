from django.shortcuts import render


def home(request):
    return render(request, "catalog/index.html")


def contacts(request):
    return render(request, "catalog/contacts.html")
