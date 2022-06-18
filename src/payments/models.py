import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from storage.models import Lease

# Create your models here.
class Payment(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 0, _("Ожидает оплаты")
        SUCCESSFUL = 1, _("Успешный")
        CANCELED = 2, _("Отклоненный")

    id = models.CharField(
        "ID оплаты от Юкассы",
        primary_key=True,
        max_length=250,
    )

    idempotence_key = models.UUIDField(
        "Ключ идемпотентности", default=uuid.uuid4, editable=False
    )

    description = models.TextField("Описание платежа")

    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        verbose_name="Элемент аренды",
        related_name="payments",
    )

    amount = models.DecimalField("Сумма платежа", max_digits=10, decimal_places=2)

    created_on = models.DateTimeField(
        "Дата создания", default=timezone.now, db_index=True
    )

    completed_on = models.DateTimeField(
        "Дата завершения", null=True, blank=True, db_index=True
    )

    status = models.SmallIntegerField(
        "Статус", choices=Status.choices, default=Status.PENDING, db_index=True
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def success(self):
        """Mark payment as successfull and lease as active"""
        self.status = Payment.Status.SUCCESSFUL
        self.completed_on = timezone.now()
        self.save()
        self.lease.status = Lease.Status.PAID
        self.lease.save()

    def cancel(self):
        """Mark payment as canceled"""
        self.status = Payment.Status.CANCELED
        self.completed_on = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.id} - {self.lease.box.code}"
