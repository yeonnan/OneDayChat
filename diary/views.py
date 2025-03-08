from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from diary.models import Diary
from diary.serializers import DiarySerializer
from chatbot.models import ChatBot, Image
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
            data["diary_image"] = {
            "image_id": diary.image.id,
            "image_url": request.build_absolute_uri(diary.image.image.url),
            }
        else:
            data["diary_image"] = None
        
        chat_images = []
        chat_msgs_with_img = ChatBot.objects.filter(
            session=diary.session, 
            image__isnull=False
        ).order_by("timestamp")

        for msg in chat_msgs_with_img:
            full_img_url = request.build_absolute_uri(msg.image.image.url)
            chat_images.append({
            "image_id": msg.image.id,
            "image_url": full_img_url
            })

        data["chat_images"] = chat_images

        return Response(data)

    # 다이어리 수정
    def put(self, request, pk):
        diary = self.get_diary(pk, request.user)

        serializer = DiarySerializer(diary, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = dict(serializer.data)
            if diary.image:
                data["diary_image"] = {
                "image_id": diary.image.id,
                "image_url": request.build_absolute_uri(diary.image.image.url),
                }
            else:
                data["diary_image"] = None
            
            chat_images = []
            chat_msgs_with_img = ChatBot.objects.filter(
            session=diary.session, 
            image__isnull=False
            ).order_by("timestamp")

            for msg in chat_msgs_with_img:
                full_img_url = request.build_absolute_uri(msg.image.image.url)
                chat_images.append({
                    "image_id": msg.image.id,
                    "image_url": full_img_url
                    })
                
            data["chat_images"] = chat_images
            
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

class DiaryImageDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        # pk = diaryId
        diary = get_object_or_404(Diary, id=pk, user=request.user)

        # 프론트에서 body로 넘긴 image_id, image_type 등
        image_id   = request.data.get("image_id")
        image_type = request.data.get("image_type")  # "DIARY" or "CHATBOT"

        if not image_id:
            return Response({"error": "image_id is required"}, status=400)

        # 1) 다이어리 image 삭제
        if image_type == "DIARY":
            if diary.image and diary.image.id == image_id:
                # diary.image를 None으로
                diary.image = None
                diary.save()
                Image.objects.filter(id=image_id).delete()
                return Response({"message": "Diary 메인 이미지 삭제 완료"})

            return Response({"error": "해당 diary image가 없거나 불일치"}, status=404)

        # 2) ChatBot 이미지 삭제
        elif image_type == "CHATBOT":
            chatbots = ChatBot.objects.filter(session=diary.session, image__id=image_id)
            if not chatbots.exists():
                return Response({"error": "해당 세션에 이 이미지가 존재하지 않습니다."}, status=404)

            # 2-1) ChatBot FK를 해제 or ChatBot 레코드 삭제 or Image 자체를 지울 지는 기획에 따라 결정
            for cb in chatbots:
                cb.image = None  # 단순히 FK만 제거
                cb.save()

            Image.objects.filter(id=image_id).delete()

            return Response({"message": "챗봇 이미지 삭제 완료"})
        
        else:
            return Response({"error": "invalid image_type"}, status=400)
