from django.shortcuts import render
from storage.models import Lease


def profile(request):
    user_leases = (
        Lease.objects.select_related("box", "box__warehouse")
        .filter(user__email=request.user.email)
        .order_by("status")
    )
    user_leases_serialized = [
        {
            "id": lease.id,
            "status": lease.get_status_display(),
            "warehouse_city": lease.box.warehouse.city,
            "warehouse_address": lease.box.warehouse.address,
            "box_number": lease.box.code,
            "lease_from": lease.created_on,
            "lease_till": lease.expires_on,
        }
        for lease in user_leases
    ]

    context = {
        "user_leases": user_leases_serialized,
    }

    return render(request, "my-rent.html", context=context)
