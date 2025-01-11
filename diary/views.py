from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 일기 리스트
    def get(self, request):
        diaries = Diary.objects.filter(user=request.user)
        if not diaries.exists():
            return Response({"message": "게시글이 없습니다."}, status=404)

        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)


class DiaryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 디테일
    def get(self, request, pk):
        try:
            diary = Diary.objects.get(id=pk, user=request.user)
            serializer = DiarySerializer(diary)
            return Response(serializer.data)
        except Diary.DoesNotExist:
            return Response({"error": "페이지를 찾을 수 없습니다."}, status=404)
