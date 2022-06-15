from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        _("имя"),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _("фамилия"),
        max_length=150,
        blank=True,
    )
    email = models.EmailField(
        _("email"),
        unique=True,
        db_index=True,
    )
    phone_number = PhoneNumberField(
        "номер телефона",
        null=True,
        unique=True,
        db_index=True,
        help_text="номер телефона в формате +79991234567",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
