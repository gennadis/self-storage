from django.shortcuts import render

from storage.models import Warehouse


def index(request):
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
