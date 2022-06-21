import random
import sys
from io import BytesIO

import qrcode
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import user_passes_test
from django.core.files.base import File
from django.db import transaction
from django.db.models import Count, Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from src.storage.forms import CreateLeaseForm, RequestDeliveryForm
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

    # Acquire lowest rate

    lowest_rate_box = (
        Box.objects.available().with_price_per_sqm().order_by("price_per_sqm").first()
    )

    lowest_rate = lowest_rate_box.price_per_sqm if lowest_rate_box else 0

    # Acquire least occupied warehouse

    warehouses_with_boxes = Box.objects.get_warehouses_with_boxes()
    free_warehouse_id = sorted(warehouses_with_boxes.items(), key=lambda kv: len(kv[1]), reverse=True)[0][0]

    free_warehouse = (
        Warehouse.objects.prefetch_related("images")
        .annotate(boxes_total=Count("boxes", distinct=True))
        .get(id=free_warehouse_id)
    )
    free_warehouse_serialized = {
        "id": free_warehouse.id,
        "boxes_total": free_warehouse.boxes_total,
        "boxes_avaliable": len(warehouses_with_boxes[free_warehouse.id]),
        "starting_rate": warehouses_with_boxes[free_warehouse.id][0]["rate"],
        "city": free_warehouse.city,
        "address": free_warehouse.address,
        "temperature": free_warehouse.temperature,
        "ceiling_height": free_warehouse.ceiling_height / 100,
        "image": free_warehouse.images.all().first().image_file.url,
    }

    return render(request, "index.html", context={
            "lowest_rate": lowest_rate,
            "free_warehouse": free_warehouse_serialized,
        },
    )


def faq(request):
    return render(request, "faq.html")


def boxes(request):
    warehouses_with_boxes = Box.objects.get_warehouses_with_boxes()

    warehouses = (
        Warehouse.objects.prefetch_related("images")
        .annotate(boxes_total=Count("boxes", distinct=True))
        .all()
    )
    warehouses_serialized = [
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
        for warehouse in warehouses if warehouses_with_boxes[warehouse.id]
    ]

    return render(request, "boxes.html", context={"warehouses": warehouses_serialized})


def avaliable_boxes(request, warehouse_id):
    warehouse = get_object_or_404(Warehouse, id=warehouse_id)

    avaliable_boxes = warehouse.boxes.available()

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


def show_lease(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    try:
        lease = (
            Lease.objects.select_related("user", "box", "box__warehouse")
            .get(id=int(lease_id))
        )
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")

    if lease.user != request.user:
        raise Http404("User cannot access this data")

    already_delivered = Delivery.objects.filter(
        lease=lease, delivery_status__in=["Completed", "In_process"]
    ).exists()

    warehouse_address = (
        f"{lease.box.warehouse.city}, {lease.box.warehouse.address}"
    )

    lease_duration = relativedelta(lease.expires_on, lease.created_on).months

    lease_serialized = {
        "id": lease.id,
        "status": lease.status,
        "status_verbose": lease.get_status_display(),
        "box_code": lease.box.code,
        "warehouse_address": warehouse_address,
        "box_area": lease.box.get_area(),
        "box_dimensions": lease.box.get_dimensions_display(),
        "box_floor": lease.box.floor,
        "box_rate": lease.box.monthly_rate,
        "expires_on": lease.expires_on,
        "total_price": lease.price,
        "duration": lease_duration,
        "already_delivered": already_delivered,
    }
    if lease.status == Lease.Status.OVERDUE:
        tolerance_period_months = 6
        lease_serialized["seize_on"] = lease.expires_on + relativedelta(
            months=+tolerance_period_months
        )

    return render(request, "lease.html", context=lease_serialized)


def get_qr_code(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    try:
        lease = Lease.objects.select_related("user").get(id=int(lease_id))
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")

    if (lease.user != request.user
        or lease.status not in [Lease.Status.PAID, Lease.Status.OVERDUE]):
        raise Http404("User cannot access this data")

    with transaction.atomic():
        random_number = random.randint(-sys.maxsize, sys.maxsize)
        qr_code_info = f"{lease.box.code}{lease.expires_on}{random_number}"
        qr_code = qrcode.make(hash(qr_code_info))
        blob = BytesIO()
        qr_code.save(blob, "JPEG")
        lease.qr_code.save(f"{qr_code_info}.jpg", File(blob))
        lease.save()

    return JsonResponse({"qr_url": lease.qr_code.url})


def cancel_lease(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    try:
        lease = Lease.objects.select_related("user").get(id=int(lease_id))
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

    create_lease_form = CreateLeaseForm(request.POST)
    if not create_lease_form.is_valid():
        raise Http404("Request data is invalid")
    
    box_code = create_lease_form.cleaned_data["code"]
    lease_duration = create_lease_form.cleaned_data["duration"]

    try:
        box = Box.objects.prefetch_related(
            Prefetch("leases", queryset=Lease.objects.active(), to_attr="active_leases")
        ).get(code=box_code)
    except Box.DoesNotExist:
        raise Http404("Box does not exist")

    if box.active_leases:
        raise Http404("Box is already leased")

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

    return render(request, "delivery_orders.html", context)


def request_delivery(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    request_delivery_form = RequestDeliveryForm(request.POST)
    if not request_delivery_form.is_valid():
        return JsonResponse(
            {
                "status": "validation_error",
                "message": "Что-то пошло не так. Повторите запрос позже.",
            }
        )
    
    lease_id = request_delivery_form.cleaned_data["lease_id"]
    address = request_delivery_form.cleaned_data["address"]

    try:
        lease = Lease.objects.select_related("user").get(id=int(lease_id))
    except Lease.DoesNotExist:
        raise Http404("Lease does not exist")

    if lease.user != request.user or lease.status != Lease.Status.PAID:
        raise Http404("User cannot access this data")

    already_requested = Delivery.objects.filter(lease=lease).exists()
    if already_requested:
        return JsonResponse(
            {
                "status": "already_exists",
                "message": (
                    "У вас уже есть необработанный заказ на доставку. "
                    "Пожалуйста, дождитесь пока с Вами свяжется наш "
                    "менеджер"
                ),
            }
        )

    delivery = Delivery.objects.create(
        lease=lease, pickup_address=address, delivery_status="Unprocessed"
    )

    return JsonResponse(
        {
            "status": "ok",
            "message": (
                "Мы приняли Ваш заказ на обработку. В близжайшее "
                "время с Вами свяжется наш менеджер, чтобы уточнить"
                " детали. Спасибо!"
            ),
        }
    )


def is_manager(user):
    return user.is_staff


@user_passes_test(is_manager, login_url="account_login")
def display_overdue_leases(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    overdue_leases = Lease.objects.overdue

    return render(
        request,
        template_name="overdue_leases.html",
        context={
            "overdue_leases": overdue_leases,
        },
    )


@user_passes_test(is_manager, login_url="account_login")
def delivery_management(request):
    delivery_orders = (
        Delivery.objects.prefetch_related("lease", "courier")
        .order_by("-registered_at")
    )
    delivery_orders_serialized = dict()
    delivery_orders_serialized["Unprocessed"] = []
    delivery_orders_serialized["In_process"] = []
    delivery_orders_serialized["Completed"] = []

    for order in delivery_orders:
        warehouse_address = (
            f"{order.lease.box.warehouse.city}, {order.lease.box.warehouse.address}"
        )
        order_serialized = {
            "id": order.id,            
            "delivery_status": order.get_delivery_status_display(),
            "warehouse_address": warehouse_address,
            "box_floor": order.lease.box.floor,
            "box_code": order.lease.box.code,
            "client_email": order.lease.user.email,
            "client_phone": order.lease.user.phone_number,
            "client_firstname": order.lease.user.first_name,
            "pickup_address": order.pickup_address,
            "registered_at": order.registered_at
        }
        if (order.delivery_status == "In_process" 
            or order.delivery_status == "Completed"):
            order_serialized["courier_firstname"] = order.courier.first_name
            order_serialized["courier_phone"] = order.courier.phone_number
            order_serialized["processed_at"] = order.processed_at
            order_serialized["comment"] = order.comment
        if order.delivery_status == "Completed":
            order_serialized["delivered_at"] = order.delivered_at
        
        delivery_orders_serialized[order.delivery_status].append(order_serialized)

    return render(request, "delivery_management.html", context={
        "delivery_orders": delivery_orders_serialized,
    })


def contacts(request):
    return render(request, template_name="contacts.html")
