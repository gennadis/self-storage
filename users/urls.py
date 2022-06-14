from django.urls import path
from users.views import dashboard

urlpatterns = [
    path("dashboard", dashboard, name="dashboard"),
]
