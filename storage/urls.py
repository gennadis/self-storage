from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("faq", views.faq, name="faq"),
    path("boxes", views.boxes, name="boxes"),
    path("rent", views.rent, name="rent"),
    path("warehouse/<int:warehouse_id>/", views.avaliable_boxes, name="avaliable_boxes")
]
