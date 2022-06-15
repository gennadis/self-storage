from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from users.models import CustomUser
from requests.models import PreparedRequest

from selfstorage.settings import BASE_URL


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

    class Meta:
        verbose_name = "склад"
        verbose_name_plural = "склады"

    def __str__(self):
        return f"{self.city}, {self.address}"


class WarehouseImage(models.Model):
    image_file = models.ImageField(
        "Изображение"
    )

    index = models.PositiveIntegerField(
        verbose_name="Приоритет при отображении",
        default=0,
        db_index=True
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        verbose_name="Склад",
        related_name="images"
    )

    class Meta:
        ordering = ["index"]

    def __str__(self) -> str:
        return f"{self.index}-{self.warehouse}"


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

    class Meta:
        verbose_name = "бокс"
        verbose_name_plural = "боксы"

    def __str__(self):
        return self.code


class Lease(models.Model):
    class Status(models.IntegerChoices):
        NOT_PAID = 0, _("Не оплачено")
        PAID = 1, _("Оплачено")
        OVERDUE = 2, _("Просрочено")
        COMPLETED = 3, _("Завершено")
        CANCELED = 4, _("Отменено")

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Арендатор",
        related_name="leases"
    )

    box = models.OneToOneField(
        Box,
        on_delete=models.CASCADE,
        verbose_name="Бокс",
        related_name="lease"
    )

    status = models.SmallIntegerField(
        "Статус",
        choices=Status.choices,
        default=Status.NOT_PAID,
        db_index=True
    )

    created_on = models.DateTimeField(
        "Дата создания",
        default=timezone.now
    )

    paid_on = models.DateTimeField(
        "Дата оплаты",
        null=True,
        blank=True,
        db_index=True
    )

    expires_on = models.DateTimeField(
        "Дата окончания аренды"
    )

    price = models.DecimalField(
        "Стоимость аренды",
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"

    def __str__(self):
        return f"{self.user.email} on box {self.box.code}"


class Link(models.Model):
    advertising_company = models.OneToOneField(
        to="AdvertisingCompany",
        verbose_name="Рекламная компания",
        related_name="link",
        on_delete=models.CASCADE,
    )
    readonly_fields = ('create_link',)

    @admin.display(description='Созданная ссылка')
    def create_link(self):
        params = {
            'ad_company': self.advertising_company.key_word,
        }
        req = PreparedRequest()
        req.prepare_url(BASE_URL, params)
        return req.url

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"


class AdvertisingCompany(models.Model):
    title = models.CharField(
        verbose_name="Название компании",
        max_length=256,
        unique=True,
    )
    key_word = models.CharField(
        verbose_name="Ключевое слово",
        max_length=256,
    )
    start_date = models.DateTimeField(
        verbose_name="Дата начала",
    )
    end_date = models.DateTimeField(
        verbose_name="Дата окончания",
    )
    #readonly_fields = ('amount',)

    clicks = models.IntegerField(
        verbose_name='Число кликов',
        default=0
    )

    # @admin.display(description='Сумма')
    # def amount(self):
    #     orders = self.orders.all()
    #     company_amount = 0
    #     for order in orders:
    #         company_amount += order.price
    #
    #     return company_amount

    class Meta:
        verbose_name = "Рекламная компания"
        verbose_name_plural = "Рекламные компании"
        ordering = ("title",)

    def __str__(self):
        return self.title
