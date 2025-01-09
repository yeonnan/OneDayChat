from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import date
from django.utils import timezone
from chatbot.models import ChatSession, ChatBot


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


class ChatBotAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 사용자와 오늘 날짜를 기준으로 세션 가져오기 or 생성
    def get_or_create_chat_session(self, user):
        today = timezone.localdate()
        # created_at__date 언더스코어 두개 : 특정 필드의 하위 속성이나 변환된 값을 필터링 하기 위해 사용
        session, created = ChatSession.objects.get_or_create(
            user=user, created_at__date=today
        )  # 세션 생성 or 가져오기
        return session

    def post(self, request):
        # 사용자 메세지 가져오기
        user_message = request.data.get("message")

        # 사용자와 연결된 세션 가져오기
        session = self.get_or_create_chat_session(request.user)

        # 사용자 메세지 저장
        ChatBot.objects.create(
            user=request.user, session=session, message_text=user_message
        )

        # 이전 대화 기록 불러오기
        previous_message = ChatBot.objects.filter(
            session=session, user=request.user
        ).order_by("timestamp")
        messages = [
            {
                "role": "system",
                "content": (
                    "너는 사용자의 친근한 대화 상대가 되어야 해. "
                    "사용자가 하루 일과나 감정을 말하면 거기에 공감하면서 반응을 해. "
                    "사용자의 대화를 항상 기억하며, 이전 대화 내용에 기반하여 응답해야 해. "
                    "대화를 이어가는데 필요한 모든 정보를 바탕으로 답변하며, 공손하지만 친근한 반말을 유지해."
                ),
            }
        ]

        for msg in previous_message:
            if msg.user == request.user:
                role = "user"  # 사용자가 보낸 메세지라면 user 역할로 추가
            else:
                role = "assistant"  # 챗봇이 보낸 메세지라면 assistant 역할로 추가
            messages.append({"role": role, "content": msg.message_text})

        # 사용자 메세지를 message 리스트에 추가
        messages.append({"role": "user", "content": user_message})

        # openai 호출
        try:
            completion = client.chat.completions.create(
                model="gpt-4o", messages=messages
            )

            # 챗봇 응답 내용 추출
            response_content = completion.choices[0].message.content

            # 챗봇 응답 db에 저장
            ChatBot.objects.create(
                user=request.user, session=session, message_text=response_content
            )

            return Response({"response": response_content})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CreateDiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        # db에서 세션 id 불러와서 openai api한테 세션을 기반으로 일기 생성해달라고 요청하기

        # 세션 id 가져오고 없으면 에러 반환
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except (
            ChatSession.DoesNotExist
        ):  # # DoesNotExist (db 조회시 객체가 존재하지 않을 때) vs KeyError (dict에서 존재하지 않는 key값 조회)
            return Response(
                {"error": "세션이 존재하지 않거나 접근 권한이 없습니다."}, status=400
            )

        # 세션 id가 있다면 세션 데이터 가져오기
        chat_message = ChatBot.objects.filter(session=session).order_by("timestamp")

        # 세션에 저장된 대화 메세지 가져오기

        # 대화 내용을 api에 전달해서 내용 반환
