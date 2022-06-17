from collections import defaultdict
from io import BytesIO
import random
import sys

import qrcode
from dateutil.relativedelta import relativedelta
from django.core.files.base import File
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from storage.models import AdvertisingCompany, Box, Delivery, Lease, Warehouse


def page_not_found(request, exception=None):
    return render(request, "404.html")


def index(request):
    ad_parameter = request.GET.get("ad_company")
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


@transaction.atomic
def create_lease_qr_code(lease):
    random_number = random.randint(-sys.maxsize, sys.maxsize)
    qr_code_info = f"{lease.box.code}{lease.expires_on}{lease.user.id}{random_number}"
    qr_code = qrcode.make(hash(qr_code_info))
    blob = BytesIO()
    qr_code.save(blob, "JPEG")
    lease.qr_code.save(f"{qr_code_info}.jpg", File(blob))
    lease.save()

    return lease.qr_code.url


def show_lease(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    try:
        lease = (
            Lease.objects.select_related("user").select_related("box").get(id=int(lease_id))
        )
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")

    if lease.user != request.user:
        raise Http404("User cannot access this data")

    already_delivered = Delivery.objects.filter(lease=lease, delivery_status="Completed").exists()

    lease_serialized = {
        "id": lease.id,
        "status": lease.get_status_display(),
        "box_code": lease.box.code,
        "box_rate": lease.box.monthly_rate,
        "expires_on": lease.expires_on,
        "total_price": lease.price,
        "already_delivered": already_delivered,
    }
    if lease.status == Lease.Status.OVERDUE:
        tolerance_period_months = 6
        lease_serialized["seize_on"] = lease.expires_on + relativedelta(months=+tolerance_period_months)

    return render(request, "lease.html", context=lease_serialized)


def get_qr_code(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    try:
        lease = (
            Lease.objects.select_related("user").select_related("box").get(id=int(lease_id))
        )
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")

    if lease.user != request.user:
        raise Http404("User cannot access this data")

    qr_url = create_lease_qr_code(lease)
    return JsonResponse({"qr_url": qr_url}) 


def cancel_lease(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    lease_id = int(request.GET.get("lease_id"))
    try:
        lease = (
            Lease.objects.select_related("user").get(id=int(lease_id))
        )
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")
    
    if lease.user != request.user or lease.status != Lease.Status.NOT_PAID:
        raise Http404("User cannot access this data")

    lease.status = Lease.Status.CANCELED
    lease.save()
    return redirect("show_lease", lease_id=lease.id)


def create_lease(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    # FIXME: Implement some validation
    box_code = request.GET.get("code")
    lease_duration = int(request.GET.get("duration"))

    active_leases = Lease.objects.filter(
        status__in=[Lease.Status.NOT_PAID, Lease.Status.PAID, Lease.Status.OVERDUE]
    )

    # FIXME: Catch ObjectDoesNotExist exception.
    box = Box.objects.prefetch_related(
        Prefetch("leases", queryset=active_leases, to_attr="active_leases")
    ).get(code=box_code)

    if box.active_leases:
        # FIXME: Display error message if box is not avaliable
        return redirect(request.META.get("HTTP_REFERER", "/"))

    lease_expiration_date = timezone.now() + relativedelta(months=+lease_duration)
    lease_total_price = box.monthly_rate * lease_duration

    new_lease = Lease.objects.create(
        user=request.user,
        box=box,
        expires_on=lease_expiration_date,
        price=lease_total_price,
    )
    return redirect("show_lease", lease_id=new_lease.id)


def delivery(request):
    context = {}
    if request.user.is_authenticated:
        courier_delivery_orders = Delivery.objects.prefetch_related(
            "lease", "courier"
        ).filter(courier=request.user)
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
        context = {"delivery_orders": delivery_orders_serialized}

    return render(request, 'delivery_orders.html', context)


def request_delivery(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    lease_id = int(request.POST.get("lease_id"))
    address = request.POST.get("address")

    try:
        lease = (
            Lease.objects.select_related("user").get(id=int(lease_id))
        )
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")
    
    if lease.user != request.user or lease.status != Lease.Status.PAID:
        raise Http404("User cannot access this data")

    already_requested = Delivery.objects.filter(lease=lease).exists()
    if already_requested:
        return JsonResponse(
            {
                "status":"already_exists", 
                "message":(
                    "У вас уже есть необработанный заказ на доставку. "
                    "Пожалуйста, дождитесь пока с Вами свяжется наш "
                    "менеджер"
                )
            }
        ) 

    delivery = Delivery.objects.create(
        lease=lease,
        pickup_address=address,
        delivery_status="Unprocessed"
        )

    return JsonResponse(
            {
                "status":"ok", 
                "message":(
                    "Мы приняли Ваш заказ на обработку. В близжайщее "
                    "время с Вами свяжется наш менеджер, чтобы уточнить"
                    " детали. Спасибо!"
                )
            }
        ) 