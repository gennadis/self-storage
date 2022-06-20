from django.urls import path

from . import views

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("register", views.register, name="register"),
]
