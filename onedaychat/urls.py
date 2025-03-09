from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.main),
    path("accounts/", include("accounts.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("diary/", include("diary.urls")),
]

# 로컬 이미지 (debug) - setting 연결
# 이미지가 들어오면 urlpatterns를 통해 모델로 연결해주는 역할
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)