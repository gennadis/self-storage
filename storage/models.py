from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Warehouse(models.Model):
    class Thumbnail(models.IntegerChoices):
        NO_THUMBNAIL = 0, _("")
        NEAR_METRO = 1, _("Рядом с метро")
        PARKING = 2, _("Парковка")
        HIGH_CEILING = 3, _("Высокие потолки")
        BIG_BOXES = 4, _("Большие боксы")


    address = models.CharField(
        "Адрес склада",
        max_length=200,
        db_index=True
    )

    city = models.CharField(
        "Город",
        max_length=40,
        db_index=True
    )

    description = models.TextField(
        "Описание"
    )

    thumbnail = models.SmallIntegerField(
        "Короткое описание",
        choices=Thumbnail.choices,
        default=Thumbnail.NO_THUMBNAIL,
        db_index=True
    )

    contact_phone = PhoneNumberField(
        "Контактный телефон"
    )

    temperature = models.SmallIntegerField(
        "Температура на складе",
        db_index=True,
        validators=[MinValueValidator(-50), MaxValueValidator(80)]
    )

    # TODO: Ограничить верхний нижний предел?
    ceiling_height = models.IntegerField(
        "Высота потолка (см)",
        db_index=True
    )

    def __str__(self):
        return f"{self.city}, {self.address}"


class Box(models.Model):
    code = models.CharField(
        "Код",
        max_length=10,
        unique=True,
        db_index=True
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name="Склад",
        related_name="boxes"
    )

    floor = models.SmallIntegerField(
        "Этаж",
        db_index=True
    )

    # TODO: Ограничить верхний нижний предел? 
    length = models.IntegerField(
        "Длина (м)",
        validators=[MinValueValidator(0)]
    )

    width = models.IntegerField(
        "Ширина (м)",
        validators=[MinValueValidator(0)]
    )

    depth = models.IntegerField(
        "Высота (м)",
        validators=[MinValueValidator(0)]
    )

    monthly_rate = models.DecimalField(
        "Стоимость аренды",
        decimal_places=2,
        max_digits=10,
        db_index=True,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.code
