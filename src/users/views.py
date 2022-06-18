from django.shortcuts import render, redirect
from storage.models import Lease
from users.forms import CustomUserCreationForm


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            custom_user = form.save()
            custom_user.save()
            return redirect("index")
    else:
        form = CustomUserCreationForm()

    return render(request, "account/signup.html", {"form": form})


def profile(request):
    user_leases = (
        Lease.objects.select_related("box", "box__warehouse")
        .filter(user=request.user)
        .order_by("status")
    )
    relevant_leases_serialized = []
    irrelevant_leases_serialized = []
    for lease in user_leases:
        lease_serialized = {
            "id": lease.id,
            "status": lease.status,
            "status_verbose": lease.get_status_display(),
            "warehouse_city": lease.box.warehouse.city,
            "warehouse_address": lease.box.warehouse.address,
            "box_number": lease.box.code,
            "lease_from": lease.created_on,
            "lease_till": lease.expires_on,
        }
        if not lease.status in [Lease.Status.CANCELED, Lease.Status.COMPLETED]:
            relevant_leases_serialized.append(lease_serialized)
        else:
            irrelevant_leases_serialized.append(lease_serialized)

    context = {
        "relevant_user_leases": relevant_leases_serialized,
        "irrelevant_user_leases": irrelevant_leases_serialized,
    }

    return render(request, "my-rent.html", context=context)
