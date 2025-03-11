from django.urls import path
from . import views


urlpatterns = [
    path("api/", views.ChatBotAPIView.as_view(), name="chatbot"),
    path("", views.ChatBotPageView.as_view(), name="T_chatbot"),
    path("create-diary/<session_id>/",views.CreateDiaryAPIView.as_view(), name="create-diary"),
    path("upload-image/", views.ImageUploadView.as_view(), name="upload-image"),
]
