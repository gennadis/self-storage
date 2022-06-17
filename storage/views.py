import os
from collections import defaultdict
from io import BytesIO

import qrcode
from django.core.files.base import ContentFile, File
from django.db.models import Prefetch, Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from selfstorage.settings import BASE_DIR, MEDIA_URL, MEDIA_ROOT
from storage.models import AdvertisingCompany, Box, Lease, Delivery, Warehouse
from users.models import CustomUser


def index(request):
    ad_parameter = request.GET.get('ad_company')
    if ad_parameter:
        now = timezone.localtime()
        try:
            advertising_company = AdvertisingCompany.objects.get(
                key_word=ad_parameter, start_date__lt=now, end_date__gt=now
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
    avaliable_boxes = (
        Box.objects.select_related("warehouse")
        .filter(~Exists(Lease.objects.filter(box=OuterRef("pk"))))
        .order_by("monthly_rate")
    )

    for box in avaliable_boxes:
        warehouses_with_boxes[box.warehouse.id].append(
            {
                "code": box.code,
                "floor": box.floor,
                "dimensions": box.get_dimensions_display(),
                "square_size": box.get_area(),
                "rate": box.monthly_rate,
            }
        )

    warehouses = (
        Warehouse.objects.prefetch_related("images")
        .annotate(boxes_total=Count("boxes", distinct=True))
        .all()
    )
    warehouses_serialized = []
    for warehouse in warehouses:
        # Do not display warehouses that have no boxes avaliable
        if not warehouses_with_boxes[warehouse.id]:
            continue

        warehouses_serialized.append(
            {
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
                "ceiling_height": warehouse.ceiling_height / 100,
                "images": [image.image_file.url for image in warehouse.images.all()],
            }
        )

    return render(request, "boxes.html", context={"warehouses": warehouses_serialized})


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
            "rate": box.monthly_rate,
        }
        for box in avaliable_boxes
    ]

    return JsonResponse({"boxes": boxes_serialized})


def create_lease_qr_code(lease):
    qr_code_info = f"{lease.box.code}{lease.expires_on}{lease.user.id}"
    qr_code = qrcode.make(qr_code_info)
    blob = BytesIO()
    qr_code.save(blob, "JPEG")
    lease.qr_code.save(f"{qr_code_info}.jpg", File(blob))
    lease.save()
    return lease.qr_code.url


def rent(request):
    user = get_object_or_404(CustomUser, email=request.user)
    context = {
        "user_leases": user.leases.all(),
    }

    return render(request, "my-rent.html", context)


def delivery(request):
    lease = Lease.objects.get(id=1)
    create_lease_qr_code(lease)
    context = {}
    if request.user.is_authenticated:
        courier_delivery_orders = Delivery.objects.prefetch_related("lease", "courier").filter(courier=request.user)
        delivery_orders_serialized = [
            {
                "order_number": delivery_order.id,
                "warehouse_city": delivery_order.lease.box.warehouse.city,
                "warehouse_address": delivery_order.lease.box.warehouse.address,
                "box_number": delivery_order.lease.box.code,
                "client_phone_number": delivery_order.lease.user.phone_number,
                "delivery_status": delivery_order.get_delivery_status_display,
                "client_first_name": delivery_order.lease.user.first_name,
                "pickup_address": delivery_order.pickup_address,
            }
            for delivery_order in courier_delivery_orders
        ]
        context = {
            "delivery_orders": delivery_orders_serialized
        }

    return render(request, 'delivery_orders.html', context)



