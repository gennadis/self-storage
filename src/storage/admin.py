from django.contrib import admin
from django.utils.html import format_html

from storage.models import (
    AdvertisingCompany,
    Box,
    Delivery,
    Lease,
    Link,
    Warehouse,
    WarehouseImage,
)


class ImageInline(admin.TabularInline):
    model = WarehouseImage

    fields = [
        "image_file",
        "image_preview",
        "index",
    ]

    readonly_fields = [
        "image_preview",
    ]

    def image_preview(self, obj):
        preview_image_height = 200
        return format_html(
            "<img src='{0}' height={1} />", obj.image_file.url, preview_image_height
        )


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    search_fields = ["address"]
    inlines = [
        ImageInline,
    ]


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    pass


@admin.register(AdvertisingCompany)
class AdvertisingCompanyAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("advertising_company", "create_link")
    list_display_links = ("create_link",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    pass


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = (
        "get_warehouse",
        "box",
        "get_user_full_name",
        "created_on",
        "expires_on",
        "status",
    )
    list_filter = ("status",)
    search_fields = (
        "box",
        "user",
    )
    ordering = (
        "status",
        "expires_on",
    )

    @admin.display(description="Пользователь")
    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description="Склад")
    def get_warehouse(self, obj):
        return obj.box.warehouse
