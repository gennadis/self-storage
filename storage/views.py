from django.shortcuts import render


def index(request):
    return render(request, "index.html")


def faq(request):
    return render(request, "faq.html")


def boxes(request):
    return render(request, "boxes.html")
