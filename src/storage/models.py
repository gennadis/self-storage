from collections import defaultdict
from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Exists, F, OuterRef
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from requests.models import PreparedRequest

from selfstorage.settings import BASE_URL
from users.models import CustomUser


class Warehouse(models.Model):
    class Thumbnail(models.IntegerChoices):
        NO_THUMBNAIL = 0, _("")
        NEAR_METRO = 1, _("Рядом с метро")
        PARKING = 2, _("Парковка")
        HIGH_CEILING = 3, _("Высокие потолки")
        BIG_BOXES = 4, _("Большие боксы")

    address = models.CharField("Адрес склада", max_length=200, db_index=True)

    city = models.CharField("Город", max_length=40, db_index=True)

    description = models.TextField("Описание")

    thumbnail = models.SmallIntegerField(
        "Короткое описание",
        choices=Thumbnail.choices,
        default=Thumbnail.NO_THUMBNAIL,
        db_index=True,
    )

    contact_phone = PhoneNumberField("Контактный телефон")

    temperature = models.SmallIntegerField(
        "Температура на складе",
        db_index=True,
        validators=[MinValueValidator(-50), MaxValueValidator(80)],
    )

    # TODO: Ограничить верхний нижний предел?
    ceiling_height = models.IntegerField("Высота потолка (см)", db_index=True)

    class Meta:
        verbose_name = "склад"
        verbose_name_plural = "склады"

    def __str__(self):
        return f"{self.city}, {self.address}"


class WarehouseImage(models.Model):
    image_file = models.ImageField("Изображение")

    index = models.PositiveIntegerField(
        verbose_name="Приоритет при отображении", default=0, db_index=True
    )

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, verbose_name="Склад", related_name="images"
    )

    class Meta:
        ordering = ["index"]

    def __str__(self) -> str:
        return f"{self.index}-{self.warehouse}"


class BoxQuerySet(models.QuerySet):
    def with_price_per_sqm(self):
        """Annotate monthly price per square meter"""
        sqm_to_sqcm_ratio = 10000
        return self.annotate(
            price_per_sqm=(
                F("monthly_rate") / ((F("width") * F("length")) / sqm_to_sqcm_ratio)
            )
        )

    def available(self):
        """Filter out Boxes with active leases"""
        return self.filter(~Exists(Lease.objects.filter(box=OuterRef("pk")).active()))

    def get_warehouses_with_boxes(self):
        """Create mapping of available boxes for each warehouse"""
        
        warehouses_with_boxes = defaultdict(list)
        avaliable_boxes = (
            self.select_related("warehouse")
            .available()
            .order_by("monthly_rate")
        )

        for box in avaliable_boxes:
            warehouses_with_boxes[box.warehouse.id].append(
                {
                    "code": box.code,
                    "floor": box.floor,
                    "dimensions": box.get_dimensions_display(),
                    "square_size": box.get_area(),
                    "rate": box.monthly_rate,
                }
            )

        return warehouses_with_boxes


class Box(models.Model):
    code = models.CharField("Код", max_length=10, unique=True, db_index=True)

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, verbose_name="Склад", related_name="boxes"
    )

    floor = models.SmallIntegerField("Этаж", db_index=True)

    # TODO: Ограничить верхний нижний предел?
    length = models.IntegerField("Длина (см)", validators=[MinValueValidator(0)])

    width = models.IntegerField("Ширина (см)", validators=[MinValueValidator(0)])

    depth = models.IntegerField("Высота (см)", validators=[MinValueValidator(0)])

    monthly_rate = models.DecimalField(
        "Стоимость аренды",
        decimal_places=2,
        max_digits=10,
        db_index=True,
        validators=[MinValueValidator(0)],
    )

    objects = BoxQuerySet.as_manager()

    class Meta:
        verbose_name = "бокс"
        verbose_name_plural = "боксы"

    def get_dimensions_display(self):
        """Get box dimension string in meters in WxLxD format"""
        width_m = self.width / 100
        length_m = self.length / 100
        depth_m = self.depth / 100
        return f"{width_m}x{length_m}x{depth_m}"

    def get_area(self):
        """Get box area in meters squared"""
        sqm_to_sqcm_ratio = 10000
        return self.width * self.length / sqm_to_sqcm_ratio

    def __str__(self):
        return self.code


class LeaseQuerySet(models.QuerySet):
    def active(self):
        """Filter active leases"""
        return self.filter(
            status__in=[Lease.Status.NOT_PAID, Lease.Status.PAID, Lease.Status.OVERDUE]
        )


class Lease(models.Model):
    class Status(models.IntegerChoices):
        NOT_PAID = 0, _("Не оплачено")
        OVERDUE = 1, _("Просрочено")
        PAID = 2, _("Оплачено")
        COMPLETED = 3, _("Завершено")
        CANCELED = 4, _("Отменено")

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Арендатор",
        related_name="leases",
    )

    box = models.ForeignKey(
        Box, on_delete=models.CASCADE, verbose_name="Бокс", related_name="leases"
    )

    status = models.SmallIntegerField(
        "Статус", choices=Status.choices, default=Status.NOT_PAID, db_index=True
    )

    created_on = models.DateField("Дата создания", default=timezone.now)

    expires_on = models.DateField("Дата окончания аренды")

    price = models.DecimalField("Стоимость аренды", max_digits=10, decimal_places=2)
    qr_code = models.ImageField(
        "QR code",
        upload_to="leaves/",
        null=True,
        blank=True,
    )

    objects = LeaseQuerySet.as_manager()

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
    readonly_fields = ("create_link",)

    @admin.display(description="Созданная ссылка")
    def create_link(self):
        params = {
            "ad_company": self.advertising_company.key_word,
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

    clicks = models.IntegerField(verbose_name="Число кликов", default=0)

    class Meta:
        verbose_name = "Рекламная компания"
        verbose_name_plural = "Рекламные компании"
        ordering = ("title",)

    def __str__(self):
        return self.title


class Delivery(models.Model):
    STATUSES = (
        ("Unprocessed", "Курьер не назначен"),
        ("In_process", "Курьер в пути"),
        ("Completed", "Груз на складе"),
    )
    lease = models.ForeignKey(
        Lease, on_delete=models.CASCADE, verbose_name="Заказ", related_name="lease"
    )
    courier = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Курьер",
        related_name="courier",
        null=True,
    )
    delivery_status = models.CharField(
        "Статус доставки заказа",
        max_length=15,
        choices=STATUSES,
        default="Unprocessed",
        db_index=True,
    )
    comment = models.TextField("Комментарий", blank=True, null=True)
    registered_at = models.DateTimeField(
        "Время назначения курьера", default=now, db_index=True
    )
    delivered_at = models.DateTimeField(
        "Время доставки груза", blank=True, null=True, db_index=True
    )
    pickup_address = models.CharField(
        "Адрес забора груза", max_length=150, db_index=True
    )

    class Meta:
        verbose_name = "Заказ на доставку"
        verbose_name_plural = "Заказы на доставку"

    def __str__(self):
        return f"Заказ {self.id} для бокса {self.lease.box.code}"
