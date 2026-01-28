from django.urls import path
from rest_framework.authtoken import views as authtoken_views

from .views import LoginView, ProfileView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login-token/", authtoken_views.obtain_auth_token, name="login-token"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
