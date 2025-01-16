from django.db import models
from django.conf import settings
from django.utils import timezone


class Image(models.Model):
    image = models.ImageField(upload_to="images/")  # 이미지 파일이 MEDIA_ROOT/images/ 경로에 저장
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} uploaded at {self.created_at}"


# 날짜별로 대화를 묶기 위한 세션 모델
class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_message_count_since_summary = models.IntegerField(default=0)


class ChatBot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    message_text = models.TextField(null=False)
    # on_delete=models.SET_NULL : 참조된 객체(Image)가 삭제되면 외래키필드 값을 null로 설정
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
