from django.urls import path

from . import views

urlpatterns = [
    path("pay/", views.make_payment, name="make payment"),
    path("confirm_payment/<int:lease_id>", views.confirm_payment, name="confirm payment"),
]
