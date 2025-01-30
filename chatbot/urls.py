from django.urls import path
from . import views


urlpatterns = [
    path("", views.ChatBotAPIView.as_view(), name="chatbot"),
    path("create-diary/<session_id>/",views.CreateDiaryAPIView.as_view(), name="create-diary"),
]
