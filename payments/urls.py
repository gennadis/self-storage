from django.urls import path

from . import views

urlpatterns = [
    path("leases/<int:lease_id>/pay", views.make_payment, name="make_payment"),
    path("payment/confirm/<str:payment_id>", views.confirm_payment, name="confirm_payment"),
]
