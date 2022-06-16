from collections import defaultdict
from django.db.models import Prefetch, Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from storage.models import AdvertisingCompany, Box, Lease

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
    warehouses_with_boxes = defaultdict(list)
    avaliable_boxes = Box.objects.select_related("warehouse").filter(
        ~Exists(Lease.objects.filter(box=OuterRef("pk")))
        ).order_by("monthly_rate")

    for box in avaliable_boxes:
        warehouses_with_boxes[box.warehouse.id].append({
            "code": box.code,
            "floor": box.floor,
            "dimensions": box.get_dimensions_display(),
            "square_size": box.get_area(),
            "rate": box.monthly_rate
        })

    warehouses = (
        Warehouse.objects.prefetch_related("images")
        .annotate(boxes_total=Count('boxes', distinct=True)).all()
    )
    warehouses_serialized = []
    for warehouse in warehouses:
        #Do not display warehouses that have no boxes avaliable
        if not warehouses_with_boxes[warehouse.id]:
            continue

        warehouses_serialized.append({
            "id": warehouse.id,
            "boxes_total": warehouse.boxes_total,
            "boxes_avaliable": len(warehouses_with_boxes[warehouse.id]),
            "starting_rate": warehouses_with_boxes[warehouse.id][0]["rate"],
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


def avaliable_boxes(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    avaliable_boxes = warehouse.boxes.filter(
        ~Exists(Lease.objects.filter(box=OuterRef("pk")))
    )

    boxes_serialized = [
        {
            "warehouse_city": warehouse.city,
            "warehouse_address": warehouse.address,
            "code": box.code,
            "floor": box.floor,
            "dimensions": box.get_dimensions_display(),
            "area": box.get_area(),
            "rate": box.monthly_rate
        }
        for box in avaliable_boxes
    ]
        
    return JsonResponse({"boxes": boxes_serialized})


def rent(request):
    # if user has rent:
    #     return render(request, "my-rent.html")
    # else:
    #     return render(request, "my-rent-empty.html")
    return render(request, "my-rent.html")
