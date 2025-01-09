from rest_framework import serializers
from .models import ChatBot, Image, ChatSession


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = "__all__"
        read_only_fields = ["id", "user", "created_at"]


class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = "__all__"
        read_only_fields = ["id", "user", "timestamp", "session"]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
