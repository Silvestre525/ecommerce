from django.urls import path
from .views import RegisterView, ProfileView
from rest_framework.authtoken import views as authtoken_views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', authtoken_views.obtain_auth_token, name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
]
