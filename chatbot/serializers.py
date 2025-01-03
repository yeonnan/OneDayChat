from rest_framework import serializers
from .models import ChatBot, Image


class ChatBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBot
        fields = '__all__'
        read_only_fields = ['id', 'user', 'timestamp']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ['id', 'created_at']