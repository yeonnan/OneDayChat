from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('signup/', views.SignupAPIView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('profile/<int:pk>/change-password/', views.ChangePasswordAPIView.as_view(), name='change-password'),
    path('profile/<int:pk>/delete/', views.DeleteAPIView.as_view(), name='delete-id')
]
