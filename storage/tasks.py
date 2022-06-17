from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from selfstorage.celery import app
from storage.models import Lease
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.core.mail import mail_admins
from django.utils import timezone
from django.db.models import F


"""Подходит конец срока аренды → Хочу об этом не забыть и забрать вещи вовремя → 
Мне приходят напоминания на почту за месяц, 2 недели, неделю и 3 дня, пока я не заберу вещи.
Не забрал вещи в срок → Хочу узнать, что с ними будет → получил письмо, 
что они будут храниться 6 месяцев по чуть повышенному тарифу, 
после чего в случае, если я их так и не заберу – я их потеряю.
Забыл забрать вещи в срок → хочу, чтобы мне об этом напомнили → получаю письма об этом раз в месяц."""


current_date = timezone.localdate(timezone.now())
tomorrow = current_date + relativedelta(days=+1)
three_days = current_date + relativedelta(days=+3)
one_week = current_date + relativedelta(weeks=+1)
two_weeks = current_date + relativedelta(weeks=+2)
one_month = current_date + relativedelta(months=+1)

LEASE_END_NOTICE_TEMPLATE = """
Срок аренды бокса номер {{ lease.box }},
расположенного по адресу: {{ lease.box.warehouse.city }} - {{ lease.box.warehouse.address }},
подходит к концу {{ lease.expires_on }}.
"""


@app.task
def send_lease_end_notice():
    active_notice_periods = [tomorrow, three_days, one_week, two_weeks, one_month]
    for notice_period in active_notice_periods:
        ending_leases = Lease.objects.prefetch_related("user", "box__warehouse").filter(
            expires_on=notice_period
        )
        for lease in ending_leases:
            template = Template(LEASE_END_NOTICE_TEMPLATE)
            send_mail(
                subject=f"Срок аренды подходит к концу!",
                message=template.render(context=Context({"lease": lease})),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lease.user.email],
                fail_silently=False,
            )
