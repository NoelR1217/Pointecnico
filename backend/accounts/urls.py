from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    CurrentUserInfoAPIView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('api/me/', CurrentUserInfoAPIView.as_view(), name='api_me'),
]

