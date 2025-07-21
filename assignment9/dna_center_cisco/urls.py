# dna_center_cisco/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("token/", views.show_token, name="token"),
    path("devices/", views.list_devices, name="devices"),
    path("interfaces/", views.device_interfaces, name="interfaces"),
]
