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
        "schedule": crontab(),
        # "schedule": crontab(hour=0, minute=0),
    },
}
