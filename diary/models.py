from django.db import models
from django.conf import settings
from chatbot.models import ChatSession, Image


class Diary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    title = models.CharField(max_length=60, null=False)
    content = models.TextField(null=False)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
