from django.shortcuts import render
from django.utils import timezone

from storage.models import AdvertisingCompany


def index(request):
    ad_parameter = request.GET.get('ad_company')
    print(ad_parameter)
    if ad_parameter:
        now = timezone.localtime()
        try:
            advertising_company = AdvertisingCompany.objects.get(
                key_word=ad_parameter,
                start_date__lt=now,
                end_date__gt=now
            )
            advertising_company.clicks += 1
            advertising_company.save()
        except AdvertisingCompany.DoesNotExist:
            advertising_company = None
    else:
        advertising_company = None

    return render(request, "index.html")


def faq(request):
    return render(request, "faq.html")


def boxes(request):
    return render(request, "boxes.html")


def rent(request):
    # if user has rent:
    #     return render(request, "my-rent.html")
    # else:
    #     return render(request, "my-rent-empty.html")
    return render(request, "my-rent.html")
