from django.urls import path
from . import views


urlpatterns = [
    path("", views.DiaryListAPIView.as_view(), name="diary-list"),
    path("<int:pk>/", views.DiaryDetailAPIView.as_view(), name="diary-detail"),
]
