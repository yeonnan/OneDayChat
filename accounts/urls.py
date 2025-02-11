from django.urls import path
from . import views


urlpatterns = [
    path("signup/", views.SignupAPIView.as_view(), name="signup"),
    path("login/", views.CookieTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("profile/<int:pk>/change-password/", views.ChangePasswordAPIView.as_view(), name="change-password"),
    path("profile/<int:pk>/delete/", views.DeleteAPIView.as_view(), name="delete-id"),
]