from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diary.models import Diary
from diary.serializers import DiarySerializer
from django.shortcuts import get_object_or_404
from django.http import Http404


class DiaryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 다이어리 리스트
    def get(self, request):
        diaries = Diary.objects.filter(user=request.user)
        if not diaries.exists():
            return Response({"message": "게시글이 없습니다."}, status=404)

        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)

class DiaryListPageView(TemplateView):
    template_name = "diary/diary_list.html"


class DiaryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_diary(self, pk, user):
        try:
            return get_object_or_404(Diary, id=pk, user=user)
        except Http404:
            raise Http404("다이어리를 찾을 수 없습니다.")

    # 디테일 조회
    def get(self, request, pk):
        diary = self.get_diary(pk, request.user) 
        serializer = DiarySerializer(diary)

        data = dict(serializer.data)
        if diary.image:
            full_url = request.build_absolute_uri(diary.image.image.url)
            data["image_url"] = full_url
        else:
            data["image_url"] = None

        return Response(data)

    # 다이어리 수정
    def put(self, request, pk):
        diary = self.get_diary(pk, request.user)

        serializer = DiarySerializer(diary, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = dict(serializer.data)
            if diary.image:
                data["image_url"] = full_url = request.build_absolute_uri(diary.image.image.url)
            else:
                data["image_url"] = None
            return Response(data)

    # 다이어리 삭제
    def delete(self, request, pk):
        diary = self.get_diary(pk, request.user)
        diary.delete()
        return Response({"message": "삭제 완료"}, status=200)

class DiaryDetailPageView(TemplateView):
    template_name = "diary/diary_detail.html"

class EditDiaryPageView(TemplateView):
    template_name = "diary/edit_diary.html"