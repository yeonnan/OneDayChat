from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from openai import OpenAI
import os
from dotenv import load_dotenv


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
    permission_classes = [IsAuthenticated]
    def post(self, request):
        # 사용자 메세지 가져오기
        user_message = request.data.get('message')

        # 사용자 메세지를 message 리스트에 추가
        message.append({'role' : 'user', 'content' : user_message})

        # openai 호출
        try:
            completion = client.chat.completions.create(
            model="gpt-4o",
            messages=message

            # django 뷰는 기본적으로 무상태(stateless)라서 대화 맥락을 유지하려면 
            # 전역 변수로 빼거나 세션, db와 같은 별도의 외부 저장소에 상태 저장이 필요하다. -> 그래서 전역 변수로 빼둠
            # messages=[
            #     {
            #         "role": "system", 
            #         "content": "사용자의 친근한 대화 상대가 되어야 해. 사용자가 하루 일과나 감정을 말하면 거기에 공감하면서 반응을 해"
            #         },
            #     {
            #         "role": "user",
            #         "content": user_message
            #     }
            # ]

        )
            # 챗봇 응답 내용 추출
            response_content = completion.choices[0].message.content

            # 챗봇 응답을 message 리스트에 추가
            message.append({'role' : 'assistant', 'content' : response_content})
            return Response({'response' : response_content})
        except Exception as e:
            return Response({'error' : str(e)}, status=500)