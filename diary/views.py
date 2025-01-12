from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diary.models import Diary
from diary.serializers import DiarySerializer


class DiaryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 다이어리 리스트
    def get(self, request):
        diaries = Diary.objects.filter(user=request.user)
        if not diaries.exists():
            return Response({"message": "게시글이 없습니다."}, status=404)

        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data)


class DiaryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 디테일 조회
    def get(self, request, pk):
        try:
            diary = Diary.objects.get(id=pk, user=request.user)
            serializer = DiarySerializer(diary)
            return Response(serializer.data)
        except Diary.DoesNotExist:
            return Response({"error": "다이어리를 찾을 수 없습니다."}, status=404)

    # 다이어리 수정
    def put(self, request, pk):
        try:
            diary = Diary.objects.get(id=pk, user=request.user)
        except Diary.DoesNotExist:
            return Response({"error": "다이어리를 찾을 수 없습니다."}, status=404)

        serializer = DiarySerializer(diary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # 다이어리 삭제
    def delete(self, request, pk):
        try:
            diary = Diary.objects.get(id=pk, user=request.user)
            diary.delete()
            return Response({"message": "삭제 완료"})
        except Diary.DoesNotExist:
            return Response({"error": "다이어리를 찾을 수 없습니다."}, status=404)
