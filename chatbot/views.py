from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from chatbot.models import ChatSession, ChatBot, Image
from diary.models import Diary
import time
from .openai_service import summarize_chat_history, chatbot_response, create_diary
from rest_framework.parsers import MultiPartParser, FormParser


class ChatBotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 사용자와 오늘 날짜를 기준으로 세션 가져오기 or 생성
    def get_or_create_chat_session(self, user):
        today = timezone.localdate()
        session = ChatSession.objects.filter(
            user=user, 
            created_at__date=today).first() 
        if session:
            return session
        # 없으면 새로 생성
        return ChatSession.objects.create(user=user)

    def post(self, request):
        # 📌 전체 처리 시간 측정 시작
        start_time_total = time.perf_counter()

        # 1. 사용자 메세지 가져오기
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "사용자 메세지가 비어있습니다."}, status=400)
        image_id = request.data.get("image_id", None)

        # 2. 사용자와 연결된 세션 가져오기
        start_time_session = time.perf_counter()  # 📌 get_or 메서드에서 db에서 세션 정보를 가져오는 시간
        session = self.get_or_create_chat_session(request.user)
        session_time_elapsed = time.perf_counter() - start_time_session  # 📌 세션 생성, 불러오기 시간 계산

        image_instance = None
        if image_id is not None:
            try:
                image_instance = Image.objects.get(id=image_id)
            except Image.DoesNotExist:
                pass

        # 사용자 메세지 저장
        ChatBot.objects.create(user=request.user, session=session, message_text=user_message, image=image_instance)

        # 4. 요약용 메세지 카운트 증가 및 체크
        session.user_message_count_since_summary += 1
        session.save()

        # 6번 이상이면 요약 진행
        if session.user_message_count_since_summary >= 6:
            chat_history = ChatBot.objects.filter(session=session).order_by("timestamp")
        else:
            chat_history = None

        try:
            if chat_history:
                summary_content = summarize_chat_history(chat_history, request.user)
                # 요약 결과를 db 저장
                ChatBot.objects.create(
                    user=session.user, 
                    session=session, 
                    message_text=f"[대화 요약]\n{summary_content}",
                    )

                # 카운트 리셋
                session.user_message_count_since_summary = 0
                session.save()

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # 5. 이전 대화 기록 불러오기
        start_time_fetch = time.perf_counter()  # 📌 이전 대화 기록을 db에서 가져오는 작업에 걸리는 시간 측정
        previous_message = ChatBot.objects.filter(session=session).order_by("timestamp")
        fetch_time_elapsed = time.perf_counter() - start_time_fetch  # 📌 이전 대화 기록 불러오기 시간 계산

        # openai 호출
        start_time_api = time.perf_counter()  # 📌 openai api 호출 시작 시점 기록
        try:
            # openai_service에 chat history + user message + user만 넘김
            response_content = chatbot_response(
                chat_history=previous_message, 
                user_message=user_message, 
                user=request.user
                )

            # 챗봇 응답 db 저장
            ChatBot.objects.create(user=request.user, session=session, message_text=response_content)
            api_time_elapsed = time.perf_counter() - start_time_api  # 📌 api 호출 시간 계산
            total_time_elapsed = time.perf_counter() - start_time_total  # 📌 전체 처리 시간 계산

            return Response(
                {
                    "response": response_content,
                    "session_id" : session.id,      
                    "새로운 채팅방 세션 생성 시간": f"{session_time_elapsed:.4f} 초",  # 세션을 생성하거나 기존 세션을 불러오는 데 걸리는 시간
                    "DB에서 대화기록 불러오는 시간": f"{fetch_time_elapsed:.4f} 초",  # 이전 대화 기록을 DB에서 가져오는데 걸리는 시간
                    "API 호출 시간": f"{api_time_elapsed:.4f} 초",  # OpenAI LLM에 요청을 보내고 응답을 받는 데 걸리는 시간
                    "전체 처리 시간": f"{total_time_elapsed:.4f} 초",  # 요청부터 응답까지 전체 소요 시간
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
        
class ChatBotPageView(TemplateView):
    template_name = "chatbot/chatbot.html"


class CreateDiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        # 1. 세션 유효성 체크
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "세션이 존재하지 않거나 접근 권한이 없습니다."}, status=404)

        # 2. 기존 대화(요약 제외) 불러오기
        chat_message = ChatBot.objects.filter(session=session).exclude(message_text__startswith="[대화 요약]").order_by("timestamp")
        if not chat_message.exists():
            return Response({"error": "세션에 대화가 없습니다."}, status=404)

        # 3. openai에게 일기 작성 요청
        try:
            diary_content = create_diary(chat_history=chat_message, user=request.user)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # 4. 다이어리 저장
        existing_diary = Diary.objects.filter(session=session, user=request.user).first()

        if existing_diary:
            # 작성된 일기가 있으면 해당 일기 업데이트
            existing_diary.content += f"{diary_content}"
            existing_diary.save()
            diary = existing_diary

        else:
            # 없다면 새로 생성
            session_date = session.created_at.date()
            title = f"{session_date}"

            diary = Diary.objects.create(
                user=request.user,
                session=session,
                title=title,
                content=diary_content,
            )

        # 5. 결과 반환
        return Response({
            "session_id": session_id, 
            "diary_id": diary.id, 
            "diary": diary_content
            }
        )


class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # 파일 받기
        uploaded_file = request.FILES.get('image', None)
        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=400)
        
        # 이미지 s3에 업로드
        img_instance = Image.objects.create(image=uploaded_file)

        # 업로드된 s3 이미지 url
        image_id = img_instance.id
        image_url = request.build_absolute_uri(img_instance.image.url)

        return Response({
            "message": "이미지 업로드 성공",
            "image_id": image_id,
            "image_url": image_url
        }, status=200)