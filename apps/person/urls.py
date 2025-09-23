from django.urls import path
from .views import RegisterView, ProfileView
from rest_framework.authtoken import views as authtoken_views

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', authtoken_views.obtain_auth_token, name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
]
