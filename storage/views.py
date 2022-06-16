from collections import defaultdict
from dateutil.relativedelta import relativedelta
from django.db.models import Prefetch, Count, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from storage.models import AdvertisingCompany, Box, Lease, Delivery, Warehouse
from users.models import CustomUser


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


def show_lease(request, lease_id):
    if not request.user.is_authenticated:
        return redirect("account_login")

    #FIXME: Implement some validation
    lease = Lease.objects.select_related("user").select_related("box").get(id=int(lease_id))
    if lease.user != request.user:
        # FIXME: Display error message if user is not owner of the lease
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    lease_seialized = {
        "id": lease.id,
        "status": lease.get_status_display(),
        "box_code": lease.box.code,
        "box_rate": lease.box.monthly_rate,
        "expires_on": lease.expires_on,
        "total_price": lease.price
    }

    return render(request, "lease.html", context=lease_seialized)


def create_lease(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    #FIXME: Implement some validation
    box_code = request.GET.get("code")
    lease_duration = int(request.GET.get("duration"))
    
    active_leases = Lease.objects.filter(
        status__in=[
            Lease.Status.NOT_PAID, 
            Lease.Status.PAID, 
            Lease.Status.OVERDUE]
        )

    #FIXME: Catch ObjectDoesNotExist exception.
    box = (
        Box.objects
        .prefetch_related(Prefetch("leases", queryset=active_leases, to_attr="active_leases"))
        .get(code=box_code)
    )

    if box.active_leases:
        # FIXME: Display error message if box is not avaliable
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    lease_expiration_date = timezone.now() + relativedelta(months=+lease_duration)
    lease_total_price = box.monthly_rate * lease_duration

    new_lease = Lease.objects.create(
        user=request.user,
        box=box,
        expires_on=lease_expiration_date,
        price=lease_total_price
    )
    return redirect("show_lease", lease_id=new_lease.id)


def profile(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

    user_leases = (
        Lease.objects.select_related("box", "box__warehouse")
        .filter(user__email=request.user.email)
        .order_by("expires_on")
    )
    user_leases_serialized = [
        {
            "counter": count,
            "warehouse_city": lease.box.warehouse.city,
            "warehouse_address": lease.box.warehouse.address,
            "box_number": lease.box.code,
            "lease_from": lease.created_on,
            "lease_till": lease.expires_on,
        }
        for count, lease in enumerate(user_leases, start=1)
    ]

    context = {
        "user_leases": user_leases_serialized,
    }

    return render(request, "my-rent.html", context=context)


def delivery(request):
    if request.user.is_authenticated:
        courier_delivery_orders = Delivery.objects.prefetch_related(
            "lease", "courier"
        ).filter(courier=request.user)
        delivery_orders_serialized = [
            {
                "order_number": order.id,
                "warehouse_city": order.lease.box.warehouse.city,
                "warehouse_address": order.lease.box.warehouse.address,
                "box_number": order.lease.box.code,
                "client_phone_number": order.lease.user.phone_number,
                "delivery_status": order.get_delivery_status_display,
                "client_first_name": order.lease.user.phone_number,
            }
            for order in courier_delivery_orders
        ]
        context = {"delivery_orders": delivery_orders_serialized}

        return render(request, "delivery_orders.html", context)
    else:
        return render(request, "delivery_orders.html")
