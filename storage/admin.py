from django.contrib import admin
from django.utils.html import format_html

from storage.models import WarehouseImage


class ImageInline(admin.TabularInline):
    model = WarehouseImage

    fields = [
        "image_file", "image_preview", "index",
    ]

    readonly_fields = [
        "image_preview",
    ]

    def image_preview(self, obj):
        preview_image_height = 200
        return format_html("<img src='{0}' height={1} />", obj.image_file.url, preview_image_height)


@admin.register
class WarehouseAdmin(admin.ModelAdmin):
    search_fields = ["address"]
