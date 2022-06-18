from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser
from storage.models import Lease


class CustomUserLeaseInline(admin.TabularInline):
    model = Lease
    extra = 0
    readonly_fields = ("status", "box", "created_on", "expires_on", "price")
    exclude = ["qr_code"]
    can_delete = False


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "phone_number",
        "first_name",
        "last_name",
        "email",
        "is_staff",
    )
    list_filter = ("is_staff",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "email",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email", "phone_number")
    ordering = ("email",)

    inlines = [CustomUserLeaseInline]


admin.site.register(CustomUser, CustomUserAdmin)
