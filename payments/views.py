import uuid
from django.shortcuts import render, redirect
from selfstorage.settings import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID
from yookassa import Configuration, Payment


def make_payment(request):
    """Use 5555 5555 5555 4444, 123, 12/22 for testing."""

    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_API_KEY

    # https://yookassa.ru/developers/using-api/interaction-format#idempotence
    idempotence_key = uuid.uuid4()

    # order_details: dict = request.POST.get("order_details")
    # price_value = order_details["price"]
    # order_description = order_details["description"]

    payment = Payment.create(
        {
            "amount": {
                # "value": f"{price_value}.00",  # API takes 10 in "10.00" format
                "value": "1.00",
                "currency": "RUB",
            },
            "confirmation": {
                "type": "embedded",
            },
            "capture": True,
            # "description": order_description,
            "description": "Some nice descritption...",
        },
        idempotency_key=str(idempotence_key),
    )
    context = {"confirmation_token": payment.confirmation.confirmation_token}

    return render(request, "payment.html", context=context)


def confirm_payment(request):
    return render(request, "payment-confirmation.html")
