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
from diary.models import Diary
import time


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
        start_time_total = (
            time.perf_counter()
        )  # 요청부터 응답까지의 전체 처리 시간 측정

        # 사용자 메세지 가져오기
        user_message = request.data.get("message")

        # 사용자와 연결된 세션 가져오기
        start_time_session = (
            time.perf_counter()
        )  # get_or 메서드에서 db에서 세션 정보를 가져오는 시간
        session = self.get_or_create_chat_session(request.user)
        session_time_elapsed = (
            time.perf_counter() - start_time_session
        )  # 세션 생성, 불러오기 시간 계산

        # 사용자 메세지 저장
        ChatBot.objects.create(
            user=request.user, session=session, message_text=user_message
        )

        # 이전 대화 기록 불러오기
        start_time_fetch = (
            time.perf_counter()
        )  # 이전 대화 기록을 db에서 가져오는 작업에 걸리는 시간 측정
        previous_message = ChatBot.objects.filter(
            session=session, user=request.user
        ).order_by("timestamp")
        fetch_time_elapsed = (
            time.perf_counter() - start_time_fetch
        )  # 이전 대화 기록 불러오기 시간 계산
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
        start_time_api = time.perf_counter()  # openai api 호출 시작 시점 기록
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
            api_time_elapsed = (
                time.perf_counter() - start_time_api
            )  # api 호출 시간 계산
            total_time_elapsed = (
                time.perf_counter() - start_time_total
            )  # 전체 처리 시간 계산

            # return Response({"response": response_content})
            return Response(
                {
                    "response": response_content,
                    "새로운 채팅방 세션 생성 시간": f"{session_time_elapsed:.4f} 초",  # 세션을 생성하거나 기존 세션을 불러오는 데 걸리는 시간
                    "DB에서 대화기록 불러오는 시간": f"{fetch_time_elapsed:.4f} 초",  # 이전 대화 기록을 DB에서 가져오는데 걸리는 시간
                    "API 호출 시간": f"{api_time_elapsed:.4f} 초",  # OpenAI LLM에 요청을 보내고 응답을 받는 데 걸리는 시간
                    "전체 처리 시간": f"{total_time_elapsed:.4f} 초",  # 요청부터 응답까지 전체 소요 시간
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class CreateDiaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        # 세션 id 가져오고 없으면 에러 반환
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except (
            ChatSession.DoesNotExist
        ):  # DoesNotExist (db 조회시 객체가 존재하지 않을 때) vs KeyError (dict에서 존재하지 않는 key값 조회)
            return Response(
                {"error": "세션이 존재하지 않거나 접근 권한이 없습니다."}, status=404
            )

        # 세션 id가 있다면 세션 데이터 가져오기
        chat_message = ChatBot.objects.filter(session=session).order_by("timestamp")
        if not chat_message.exists():
            return Response({"error": "세션에 대화가 없습니다."}, status=404)

        # 대화 내용을 api에 전달해서 내용 반환
        messages = [
            {
                "role": "system",
                "content": (
                    "너는 세션에 있는 대화 내용을 바탕으로 일기를 작성하는 비서야."
                    "다른 감정과 불필요한 말은 추가하지 말고 사용자가 대화한 내용을 기반으로 일기를 작성해"
                    "인칭이 필요하다면 1인칭으로 유저가 작성한 것이라 생각하고 작성해"
                ),
            }
        ]

        # 이전 메세지 순회
        for msg in chat_message:
            # 메세지를 작성한 사용자가 현재 요청을 보낸 사용자라면
            if msg.user == request.user:
                role = "user"  # 역할을 user로 설정
            else:
                role = "assistant"
            messages.append({"role": role, "content": msg.message_text})

        # api 호출
        try:
            completion = client.chat.completions.create(
                model="gpt-4o", messages=messages, temperature=0.7
            )

            # 생성된 일기 내용
            diary_content = completion.choices[0].message.content

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # 세션 날짜 -> 제목
        session_date = session.created_at.date()
        title = f"{session_date}"

        # 생성된 일기를 diary 모델에 저장
        diary = Diary.objects.create(
            user=request.user,
            session=session,
            title=title,
            content=diary_content,
        )

        # 결과 반환
        return Response(
            {"session_id": session_id, "diary_id": diary.id, "diary": diary_content}
        )
