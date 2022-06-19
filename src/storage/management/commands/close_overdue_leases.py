from django.core.management.base import BaseCommand, CommandError

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone

from storage.models import Lease


class Command(BaseCommand):
    help = "Close overdue leases."

    def handle(self, *args, **options):
        current_date = timezone.localdate(timezone.now())
        overdue_leases = Lease.objects.filter(
            expires_on__lte=current_date, status=Lease.Status.PAID
        ).update(status=Lease.Status.OVERDUE)
