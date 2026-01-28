from django.urls import path

from . import views

urlpatterns = [
    path("debug/auth/", views.debug_auth, name="debug_auth"),
    path("debug/system-info/", views.system_info, name="system_info"),
]
