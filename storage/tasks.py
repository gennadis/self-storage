from django.template import Template, Context
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from selfstorage.celery import app
from storage.models import Lease
from django.conf import settings


REPORT_TEMPLATE = """
Here's your current leases:
 
{% for lease in leases %}
        "{{ lease.box }}": {{ lease.created_on }} - {{ lease.expires_on }}

{% endfor %}
"""


@app.task
def send_leases_report():
    for user in get_user_model().objects.all():
        user_leases = Lease.objects.filter(user=user)
        if not user_leases:
            continue

        template = Template(REPORT_TEMPLATE)
        send_mail(
            subject="Your current leases",
            message=template.render(context=Context({"leases": user_leases})),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
