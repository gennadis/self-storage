from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

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
    list_display = (
        "delivery_status",
        "get_client_phone",
        "pickup_address",
        "get_warehouse_address",
        "get_box_code",
        "courier",
        "registered_at",
        "processed_at",
        "delivered_at",
    )
    fields = (
        "lease",
        "courier",
        "delivery_status",
        "pickup_address",
        "get_warehouse_address",
        "comment",
        "registered_at",
        "processed_at",
        "delivered_at",
    )

    list_filter = ("delivery_status",)

    ordering = (
        "registered_at",
        "processed_at",
        "delivered_at",
    )

    readonly_fields = ("get_warehouse_address",)

    @admin.display(description="Адрес склада")
    def get_warehouse_address(self, obj):
        return (
            f"{obj.lease.box.warehouse.city},"
            f"{obj.lease.box.warehouse.address}"
            f" - {obj.lease.box.floor} эт."
        )

    @admin.display(description="Телефон клиента")
    def get_client_phone(self, obj):
        return f"{obj.lease.user.phone_number}"

    @admin.display(description="Код Бокса")
    def get_box_code(self, obj):
        return f"{obj.lease.box.code}"

    def response_post_save_change(self, request, obj):
        # Redirect back if request comes from manager view

        generic_response = super().response_post_save_change(request, obj)
        redirect_url = request.GET.get("next")
        return (
            HttpResponseRedirect(redirect_url)
            if redirect_url and url_has_allowed_host_and_scheme(redirect_url, None)
            else generic_response
        )


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = (
        "get_warehouse",
        "box",
        "get_user_full_name",
        "get_user_phone_number",
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

    @admin.display(description="Номер телефона")
    def get_user_phone_number(self, obj):
        return obj.user.phone_number
