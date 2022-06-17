from django.shortcuts import render, redirect
from storage.models import Lease
from users.forms import CustomUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            custom_user = form.save()
            custom_user.save()
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'account/signup.html', {'form': form})


def profile(request):
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
