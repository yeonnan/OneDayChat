from django.urls import path
from . import views


urlpatterns = [
    path("userinfo/", views.UserInfoAPIView.as_view(), name="userinfo"),
    path("api/signup/", views.SignupAPIView.as_view(), name="signup"),
    path("signup/", views.SignupPageView.as_view(), name="T_signup"),
    path("api/login/", views.CookieTokenObtainPairView.as_view(), name="login"),
    path("login/", views.LoginPageView.as_view(), name="T_login"),
    path("token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("api/profile/<int:pk>/change-password/", views.ChangePasswordAPIView.as_view(), name="change-password"),
    path("profile/<int:pk>/change-password/", views.ChangePasswordPageView.as_view(), name="T_change-password"),
    path("api/profile/<int:pk>/delete/", views.DeleteAPIView.as_view(), name="delete-id"),
    path("profile/<int:pk>/delete/", views.DeletePageView.as_view(), name="T_delete-id"),
]