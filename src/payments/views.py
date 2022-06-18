import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from selfstorage.settings import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID
from storage.models import Lease
from .models import Payment
from yookassa import Configuration, Payment as YooPayment


def make_payment(request, lease_id):
    """Use 5555 5555 5555 4444, 123, 12/22 for testing."""

    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_API_KEY

    # https://yookassa.ru/developers/using-api/interaction-format#idempotence
    lease = get_object_or_404(Lease, id=int(lease_id))

    # If there is already a pending payment use idempotence to repeat payment attempt
    try:
        pending_payment = Payment.objects.get(lease=lease, status=Payment.Status.PENDING)
    except Payment.DoesNotExist:
        pending_payment = None

    if pending_payment:
        payment_amount = pending_payment.amount
        payment_description = pending_payment.description
        idempotence_key = pending_payment.idempotence_key
    else:
        payment_amount = lease.price
        payment_description = f"Оплата аренды бокса №{lease.box.code} до {lease.expires_on}"
        idempotence_key = uuid.uuid4()

    payment = YooPayment.create(
        {
            "amount": {
                "value": str(payment_amount),
                "currency": "RUB",
            },
            "confirmation": {
                "type": "embedded",
            },
            "capture": True,
            "description": payment_description,
        },
        idempotency_key=str(idempotence_key),
    )

    # Create new payment entry for the initial payment attempt

    if not pending_payment:
        Payment.objects.create(
            id=payment.id,
            idempotence_key=idempotence_key,
            lease=lease,
            description=payment_description,
            amount=payment_amount
        )

    context = {
        "confirmation_token": payment.confirmation.confirmation_token,
        "payment_id": payment.id,
        "return_url": request.build_absolute_uri(reverse("confirm_payment", kwargs={"payment_id": payment.id}))
    }

    return render(request, "payment.html", context=context)


def confirm_payment(request, payment_id):
    payment_attmept = get_object_or_404(Payment, id=payment_id)
    lease = payment_attmept.lease

    # Ignore confirmation calls for leases that are already proccessed
    if lease.status != Lease.Status.NOT_PAID:
        return redirect("show_lease", lease_id=lease.id)

    payment = YooPayment.find_one(payment_id)
    if payment.status == "succeeded":
        payment_attmept.success()
    elif payment.status == "canceled":
        payment_attmept.cancel()
    else:
        # User manually attempted to access confirm_payment view
        return redirect("make_payment", lease_id=lease.id)

    return redirect("show_lease", lease_id=lease.id)
