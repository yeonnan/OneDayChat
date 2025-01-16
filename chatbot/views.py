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
        session, created = ChatSession.objects.get_or_create(user=user, created_at__date=today)  # 세션 생성 or 가져오기
        return session

    def post(self, request):
        # 📌 전체 처리 시간 측정 시작
        start_time_total = time.perf_counter()

        # 1. 사용자 메세지 가져오기
        user_message = request.data.get("message")

        # 2. 사용자와 연결된 세션 가져오기
        start_time_session = time.perf_counter()  # 📌 get_or 메서드에서 db에서 세션 정보를 가져오는 시간
        session = self.get_or_create_chat_session(request.user)
        session_time_elapsed = time.perf_counter() - start_time_session  # 📌 세션 생성, 불러오기 시간 계산

        # 사용자 메세지 저장
        ChatBot.objects.create(user=request.user, session=session, message_text=user_message)

        # 4. 요약용 메세지 카운트 증가 및 체크
        session.user_message_count_since_summary += 1
        session.save()

        # summary_messages 기본 설정
        summary_messages = []

        # 3번 이상이면 요약 진행
        if session.user_message_count_since_summary >= 6:
            chat_history = ChatBot.objects.filter(session=session).order_by("timestamp")

            # 요약 프롬프트
            summary_messages = [
                {
                    "role": "system",
                    "content": (
                        "너는 대화 내용을 요약하는 비서야. 대화의 핵심 내용을 간결하고 명확하게 정리해" "간단한 인사말('안녕', '잘지냈어?')은 제외하고 주요 질문과 답변만 요약해"
                    ),
                }
            ]
            for msg in chat_history:
                if msg.user == session.user:
                    role = "user"
                else:
                    role = "assistant"
                summary_messages.append({"role": role, "content": msg.message_text})

        # 요약 api 호출
        try:
            # summary_messages가 비어 있지 않은 경우에만 호출
            if summary_messages:
                completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=summary_messages)
                summary_content = completion.choices[0].message.content

                # 요약 결과를 assisntant 메세지로 저장
                ChatBot.objects.create(user=session.user, session=session, message_text=f"[대화 요약]\n{summary_content}")

                # 카운트 리셋
                session.user_message_count_since_summary = 0
                session.save()

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # 이전 대화 기록 불러오기
        start_time_fetch = time.perf_counter()  # 📌 이전 대화 기록을 db에서 가져오는 작업에 걸리는 시간 측정
        previous_message = ChatBot.objects.filter(session=session).order_by("timestamp")
        fetch_time_elapsed = time.perf_counter() - start_time_fetch  # 📌 이전 대화 기록 불러오기 시간 계산

        # 6. 챗봇 llm
        messages = [
            {
                "role": "system",
                "content": (
                    "너는 사용자의 친근한 대화 상대야. 사용자가 하루 일과나 감정을 말하면 공감하며 반응해. "
                    "이전 대화를 기억하고 그에 맞는 응답을 하며, 공손하지만 친근한 반말로 답변해."
                ),
            }
        ]

        # 이전 대화 기록 추가
        for msg in previous_message:
            if msg.user == request.user:
                role = "user"  # 사용자가 보낸 메세지라면 user 역할로 추가
            else:
                role = "assistant"  # 챗봇이 보낸 메세지라면 assistant 역할로 추가
            messages.append({"role": role, "content": msg.message_text})

        # 사용자 메세지를 message 리스트에 추가
        # messages.append({"role": "user", "content": user_message})

        # 사용자 메세지 추가
        user_message = request.data.get("message")
        if user_message:
            messages.append({"role": "user", "content": user_message})  # 사용자 메시지 추가
        else:
            return Response({"error": "사용자 메시지가 비어 있습니다."}, status=400)  # 사용자 메시지가 없을 경우 에러 반환

        # openai 호출
        start_time_api = time.perf_counter()  # 📌 openai api 호출 시작 시점 기록
        try:
            completion = client.chat.completions.create(model="gpt-4o", messages=messages)

            # 챗봇 응답 내용 추출
            response_content = completion.choices[0].message.content

            # 챗봇 응답 db에 저장
            ChatBot.objects.create(user=request.user, session=session, message_text=response_content)
            api_time_elapsed = time.perf_counter() - start_time_api  # 📌 api 호출 시간 계산
            total_time_elapsed = time.perf_counter() - start_time_total  # 📌 전체 처리 시간 계산

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
        except ChatSession.DoesNotExist:  # DoesNotExist (db 조회시 객체가 존재하지 않을 때) vs KeyError (dict에서 존재하지 않는 key값 조회)
            return Response({"error": "세션이 존재하지 않거나 접근 권한이 없습니다."}, status=404)

        # 세션 id가 있다면 세션 데이터 가져오기 (원본 메세지만)
        chat_message = ChatBot.objects.filter(session=session).exclude(message_text__startswith="[대화 요약]").order_by("timestamp")
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
            completion = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.7)

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
        return Response({"session_id": session_id, "diary_id": diary.id, "diary": diary_content})
