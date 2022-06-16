from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("faq", views.faq, name="faq"),
    path("boxes", views.boxes, name="boxes"),
    path("lease", views.create_lease, name="create_lease"),
    path("leases/<int:lease_id>", views.show_lease, name="show_lease"),
    path(
        "warehouse/<int:warehouse_id>/", views.avaliable_boxes, name="avaliable_boxes"
    ),
    path("delivery", views.delivery, name="delivery_orders"),
]
