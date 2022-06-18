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
    "send_leases_report_daily_at_midnight": {
        "task": "storage.tasks.send_lease_end_notice",
        # "schedule": crontab(minute=15),
        "schedule": crontab(hour=0, minute=0),
    },
    "check_lease_payment_status_every_minute": {
        "task": "storage.tasks.check_lease_payment_status",
        "schedule": crontab(),
        # "schedule": crontab(hour=0, minute=0),
    },
}
