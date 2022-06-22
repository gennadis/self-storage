from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.validators import validate_email

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update({"placeholder": "Имя"})
        self.fields["last_name"].widget.attrs.update({"placeholder": "Фамилия"})
        self.fields["phone_number"].widget.attrs.update(
            {"placeholder": "Номер телефона"}
        )
        self.fields["email"].widget.attrs.update({"placeholder": "email"})
        self.fields["password1"].widget.attrs.update({"placeholder": "Пароль"})
        self.fields["password2"].widget.attrs.update(
            {"placeholder": "Подтверждение пароля"}
        )

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number", "email"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ["email"]

    def clean(self):
        email = validate_email(self.cleaned_data.get("email"))

        return self.cleaned_data
