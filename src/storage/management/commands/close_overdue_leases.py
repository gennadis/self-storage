from django.core.management.base import BaseCommand, CommandError

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone

from storage.models import Lease


LEASE_ENDED_NOTICE_TEMPLATE = """
Уведомление об окончании срока аренды:

Срок аренды бокса номер {{ lease.box }},
расположенного по адресу: {{ lease.box.warehouse.city }} - {{ lease.box.warehouse.address }},
подошел к концу {{ lease.expires_on }}.

Свяжитесь с менеджером склада для уточнения стоимости дальнейшего хранения имущества.
Имущество будет храниться не более 6 месяцев с даты окончания срока аренды.
"""


class Command(BaseCommand):
    help = "Close overdue leases and send Lease ended notice."

    def handle(self, *args, **options):
        current_date = timezone.localdate(timezone.now())
        new_overdue_leases = Lease.objects.filter(
            expires_on__lte=current_date, status=Lease.Status.PAID
        )

        for lease in new_overdue_leases:
            template = Template(LEASE_ENDED_NOTICE_TEMPLATE)
            send_mail(
                subject=f"Срок аренды подошел к концу!",
                message=template.render(context=Context({"lease": lease})),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lease.user.email],
                fail_silently=False,
            )

        new_overdue_leases.update(status=Lease.Status.OVERDUE)
