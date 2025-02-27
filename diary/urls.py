from django.urls import path
from . import views


urlpatterns = [
    path("api/", views.DiaryListAPIView.as_view(), name="diary-list"),
    path("", views.DiaryListPageView.as_view(), name="T_diary-list"),
    path("api/<int:pk>/", views.DiaryDetailAPIView.as_view(), name="diary-detail"),
    path("<int:pk>/", views.DiaryDetailPageView.as_view(), name="T_diary_detail"),
    path("<int:pk>/edit/", views.EditDiaryPageView.as_view(), name="T_edit-diary"),
]
