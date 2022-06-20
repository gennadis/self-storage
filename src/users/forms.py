from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.validators import validate_email

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone_number", "email"]


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ["email"]

    def clean(self):
        email = validate_email(self.cleaned_data.get('email'))

        return self.cleaned_data
