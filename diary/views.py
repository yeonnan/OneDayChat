from django.shortcuts import render
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


class DiaryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_diary(self, pk, user):
        try:
            return get_object_or_404(Diary, id=pk, user=user)
        except Http404:
            raise Http404("다이어리를 찾을 수 없습니다.")

    # 디테일 조회
    def get(self, request, pk):
        diary = self.get_diary(pk, request.user)  # diary pk에 해당하는 게시글 가져오기
        serializer = DiarySerializer(diary)
        return Response(serializer.data)

    # 다이어리 수정
    def put(self, request, pk):
        diary = self.get_diary(pk, request.user)
        serializer = DiarySerializer(diary, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    # 다이어리 삭제
    def delete(self, request, pk):
        diary = self.get_diary(pk, request.user)
        diary.delete()
        return Response({"message": "삭제 완료"}, status=200)
