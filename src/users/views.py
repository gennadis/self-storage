import phonenumbers
from django.shortcuts import redirect, render

from storage.models import Lease
from users.forms import CustomUserChangeForm, CustomUserCreationForm
from users.models import CustomUser


def signup_confirmation(request):
    return render(request, "account/signup_confirmation.html")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            custom_user = form.save()
            custom_user.save()
            return redirect("signup_confirmation")
    else:
        form = CustomUserCreationForm()

    return render(request, "account/signup.html", {"form": form})


def profile(request):
    if not request.user.is_authenticated:
        return redirect("account_login")

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

    form = CustomUserChangeForm()
    context = {
        "relevant_user_leases": relevant_leases_serialized,
        "irrelevant_user_leases": irrelevant_leases_serialized,
        "form": form,
    }

    user = CustomUser.objects.get(email=request.user.email)

    if request.method == "POST":
        changed_form = CustomUserChangeForm(request.POST)
        if changed_form.is_valid():
            user.email = changed_form.cleaned_data.get("email")
            phone_number = phonenumbers.parse(
                changed_form.data.get("phone_number"), "RU"
            )

            if not phonenumbers.is_valid_number(phone_number):
                context["not_valid_phone_number"] = "Введите верный номер телефона"

                return render(request, "my-rent.html", context=context)
            else:
                user.phone_number = phone_number
                user.save()

                context["user"] = user

                return render(request, "my-rent.html", context=context)
        else:
            context["user"] = user

            return render(request, "my-rent.html", context=context)

    return render(request, "my-rent.html", context=context)
