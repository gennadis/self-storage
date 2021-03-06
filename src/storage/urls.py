from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("faq", views.faq, name="faq"),
    path("boxes", views.boxes, name="boxes"),
    path("contacts", views.contacts, name="contacts"),
    path("lease", views.create_lease, name="create_lease"),
    path("leases/<int:lease_id>", views.show_lease, name="show_lease"),
    path("leases/<int:lease_id>/qrcode", views.get_qr_code, name="get_qr_code"),
    path("leases/<int:lease_id>/cancel", views.cancel_lease, name="cancel_lease"),
    path(
        "warehouse/<int:warehouse_id>/", views.avaliable_boxes, name="avaliable_boxes"
    ),
    path("request_delivery/", views.request_delivery, name="request_delivery"),
    path("delivery/courier", views.delivery, name="delivery_orders"),
    path("delivery/management", views.delivery_management, name="delivery_management"),
    path("overdue", views.display_overdue_leases, name="overdue leases"),
]
