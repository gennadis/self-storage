import uuid
from django.shortcuts import get_object_or_404, render, redirect
from selfstorage.settings import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID
from storage.models import Lease
from yookassa import Configuration, Payment


def make_payment(request):
    """Use 5555 5555 5555 4444, 123, 12/22 for testing."""

    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_API_KEY

    # https://yookassa.ru/developers/using-api/interaction-format#idempotence
    idempotence_key = uuid.uuid4()

    # order_details: dict = request.POST.get("order_details")
    price_value = request.POST.get("order_price").replace(",",".")
    order_description = request.POST.get("order_description")
    lease_id = request.POST.get("lease_id")

    payment = Payment.create(
        {
            "amount": {
                "value": f"{price_value}",
                "currency": "RUB",
            },
            "confirmation": {
                "type": "embedded",
            },
            "capture": True,
            "description": order_description,
        },
        idempotency_key=str(idempotence_key),
    )
    context = {
        "confirmation_token": payment.confirmation.confirmation_token,
        "lease_id": lease_id
    }

    # Save Yookassa payment ID for status checking
    lease = get_object_or_404(Lease, id=int(lease_id))
    lease.payment_id = payment.id
    lease.status = Lease.Status.NOT_PAID
    lease.save()

    return render(request, "payment.html", context=context)


def confirm_payment(request, lease_id):
    lease = get_object_or_404(Lease, id=int(lease_id))

    lease.save()

    return redirect("show_lease", lease_id=lease.id)
