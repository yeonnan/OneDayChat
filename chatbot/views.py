from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import date
from chatbot.models import ChatSession, ChatBot
from chatbot.serializers import ChatBotSerializer, ChatSessionSerializer


load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

message = [
    {
        "role": "system",
        "content": "사용자의 친근한 대화 상대가 되어야 해. 사용자가 하루 일과나 감정을 말하면 거기에 공감하면서 반응을 해."
    }
]


class ChatBotAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 사용자와 오늘 날짜를 기준으로 세션 가져오기 or 생성
    def get_or_create_chat_session(self, user):
        today = date.today()    # 오늘 날짜
        session, created = ChatSession.objects.get_or_create(user=user, created_at=today)   # 세션 생성 or 가져오기
        return session

    def post(self, request):
        # 사용자 메세지 가져오기
        user_message = request.data.get('message')


        # 사용자와 연결된 세션 가져오기
        session = self.get_or_create_chat_session(request.user)     # 세션 가져오기

        # 사용자 메세지 저장
        ChatBot.objects.create(
            user = request.user,
            session = session,
            message_text = user_message
        )


        # 사용자 메세지를 message 리스트에 추가
        global message
        message.append({'role' : 'user', 'content' : user_message})

        # openai 호출
        try:
            completion = client.chat.completions.create(
            model="gpt-4o",
            messages=message
            )

            # 챗봇 응답 내용 추출
            response_content = completion.choices[0].message.content

            # 챗봇 응답을 message 리스트에 추가
            message.append({'role' : 'assistant', 'content' : response_content})

            # 챗봇 응답 db에 저장
            ChatBot.objects.create(
                user = request.user,
                session = session,
                message_text = response_content
            )

            return Response({'response' : response_content})
        except Exception as e:
            return Response({'error' : str(e)}, status=500)
        

class ChatSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)