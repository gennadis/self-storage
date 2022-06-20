import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "selfstorage.settings")

app = Celery("storage")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


app.conf.beat_schedule = {
    # Не забрал вещи в срок → Хочу узнать, что с ними будет →
    # получил письмо, что они будут храниться 6 месяцев по чуть повышенному тарифу,
    # после чего в случае, если я их так и не заберу – я их потеряю.
    "close_overdue_leases": {
        "task": "storage.tasks.close_overdue_leases",
        "schedule": crontab(0),
        # "schedule": crontab(hour=0, minute=0),
    },
    # Подходит конец срока аренды → Хочу об этом не забыть и забрать вещи вовремя
    # → Мне приходят напоминания на почту за месяц, 2 недели, неделю и 3 дня, пока я не заберу вещи.
    "send_notice_lease_ends_soon": {
        "task": "storage.tasks.send_notice_lease_ends_soon",
        "schedule": crontab(0),
        # "schedule": crontab(hour=12, minute=0),
    },
    # Забыл забрать вещи в срок → хочу, чтобы мне об этом напомнили
    # → получаю письма об этом раз в месяц.
    "send_notice_lease_ended": {
        "task": "storage.tasks.send_notice_lease_ended",
        # "schedule": crontab(0, 0, day_of_month="1"),
        "schedule": crontab(0),
    },
    # "check_lease_payment_status_every_minute": {
    #     "task": "storage.tasks.check_lease_payment_status",
    #     "schedule": crontab(),
    # "schedule": crontab(hour=0, minute=0),
    # },
}
