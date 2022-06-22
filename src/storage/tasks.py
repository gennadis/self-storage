from celery.utils.log import get_task_logger
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins, send_mail
from django.core.management import call_command
from django.db.models import F
from django.template import Context, Template
from django.utils import timezone
from yookassa import Configuration, Payment

from selfstorage.celery import app
from selfstorage.settings import YOOKASSA_API_KEY, YOOKASSA_SHOP_ID
from storage.models import Lease

logger = get_task_logger(__name__)


@app.task
def close_overdue_leases():
    call_command(
        "close_overdue_leases",
    )


@app.task
def send_notice_lease_ended():
    call_command(
        "send_notice_lease_ended",
    )


@app.task
def send_notice_lease_ends_soon():
    call_command(
        "send_notice_lease_ends_soon",
    )


@app.task
def check_lease_payment_status():
    Configuration.secret_key = YOOKASSA_API_KEY
    Configuration.account_id = YOOKASSA_SHOP_ID

    unpaid_leases = Lease.objects.filter(status=0)
    for lease in unpaid_leases:
        lease_payment = Payment.find_one(lease.payment_id)
        if lease_payment.status == "succeeded":
            lease.status = 2
            lease.save()
