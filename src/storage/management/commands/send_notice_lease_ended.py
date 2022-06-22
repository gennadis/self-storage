from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.template import Context, Template
from django.utils import timezone

from storage.models import Lease

LEASE_ENDED_NOTICE_TEMPLATE = """
Ежемесячное напоминание:

Срок аренды бокса номер {{ lease.box }},
расположенного по адресу: {{ lease.box.warehouse.city }} - {{ lease.box.warehouse.address }},
окончен {{ lease.expires_on }}.

Имущество будет храниться не более 6 месяцев с даты окончания срока аренды.
"""


class Command(BaseCommand):
    help = "Send Lease ended notice."

    def handle(self, *args, **options):
        for lease in Lease.objects.overdue():
            template = Template(LEASE_ENDED_NOTICE_TEMPLATE)
            send_mail(
                subject=f"Срок аренды подошел к концу!",
                message=template.render(context=Context({"lease": lease})),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lease.user.email],
                fail_silently=False,
            )
