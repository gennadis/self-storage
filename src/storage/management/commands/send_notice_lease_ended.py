from django.core.management.base import BaseCommand, CommandError

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template import Context, Template
from django.utils import timezone

from storage.models import Lease

"""Не забрал вещи в срок → Хочу узнать, что с ними будет → получил письмо, 
что они будут храниться 6 месяцев по чуть повышенному тарифу, 
после чего в случае, если я их так и не заберу – я их потеряю.
Забыл забрать вещи в срок → хочу, чтобы мне об этом напомнили → получаю письма об этом раз в месяц."""


LEASE_ENDED_NOTICE_TEMPLATE = """
Срок аренды бокса номер {{ lease.box }},
расположенного по адресу: {{ lease.box.warehouse.city }} - {{ lease.box.warehouse.address }},
окончен {{ lease.expires_on }}.

Имущество будет храниться не более 6 месяцев с даты окончания срока аренды.
"""


class Command(BaseCommand):
    help = "Send Lease ended notice."

    def handle(self, *args, **options):
        overdue_leases = Lease.objects.prefetch_related(
            "user", "box__warehouse"
        ).filter(status=Lease.Status.OVERDUE)

        for lease in overdue_leases:
            template = Template(LEASE_ENDED_NOTICE_TEMPLATE)
            send_mail(
                subject=f"Срок аренды подошел к концу!",
                message=template.render(context=Context({"lease": lease})),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lease.user.email],
                fail_silently=False,
            )
