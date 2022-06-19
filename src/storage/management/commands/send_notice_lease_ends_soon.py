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


LEASE_ENDS_SOON_NOTICE_TEMPLATE = """
Срок аренды бокса номер {{ lease.box }},
расположенного по адресу: {{ lease.box.warehouse.city }} - {{ lease.box.warehouse.address }},
подходит к концу {{ lease.expires_on }}.
"""


class Command(BaseCommand):
    help = "Send Lease ends soon notice."

    def handle(self, *args, **options):
        current_date = timezone.localdate(timezone.now())

        for expiration_date in self.get_notice_periods(current_date):
            ending_leases = Lease.objects.prefetch_related(
                "user", "box__warehouse"
            ).filter(expires_on=expiration_date, status=Lease.Status.PAID)

            for lease in ending_leases:
                template = Template(LEASE_ENDS_SOON_NOTICE_TEMPLATE)
                send_mail(
                    subject=f"Срок аренды подходит к концу!",
                    message=template.render(context=Context({"lease": lease})),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[lease.user.email],
                    fail_silently=False,
                )

    @staticmethod
    def get_notice_periods(current_date):
        three_days = current_date + relativedelta(days=+3)
        one_week = current_date + relativedelta(weeks=+1)
        two_weeks = current_date + relativedelta(weeks=+2)
        one_month = current_date + relativedelta(months=+1)

        return three_days, one_week, two_weeks, one_month
