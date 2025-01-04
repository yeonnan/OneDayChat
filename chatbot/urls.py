from django.urls import path
from . import views


urlpatterns = [
    path('', views.ChatBotAPIView.as_view(), name='chatbot'),
]
