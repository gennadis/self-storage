from django.shortcuts import render
from django.utils import timezone

from storage.models import AdvertisingCompany

from storage.models import Warehouse


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
    warehouses = Warehouse.objects.prefetch_related("images").all()
    warehouses_serialized = []
    for warehouse in warehouses:
        warehouses_serialized.append({
            "id": f"wh{warehouse.id}",
            "city": warehouse.city,
            "address": warehouse.address,
            "description": warehouse.description,
            "thumbnail": warehouse.get_thumbnail_display(),
            "contact_phone": warehouse.contact_phone,
            "temperature": warehouse.temperature,
            "ceiling_height": warehouse.ceiling_height/100,
            "images": [image.image_file.url for image in warehouse.images.all()]
        })

    return render(request, "boxes.html", context={
        "warehouses": warehouses_serialized
    })


def rent(request):
    # if user has rent:
    #     return render(request, "my-rent.html")
    # else:
    #     return render(request, "my-rent-empty.html")
    return render(request, "my-rent.html")
