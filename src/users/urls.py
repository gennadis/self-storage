from django.urls import path

from . import views

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("register", views.register, name="register"),
    path("signup_confirmation", views.signup_confirmation, name="signup_confirmation"),
]
