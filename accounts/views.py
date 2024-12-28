from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.serializers import UserSerializer


class SignupAPIView(APIView):
    # 회원가입
    '''
    닉네임, 이메일 db에서 중복 검사 진행 후 존재하면 400 -> 닉네임, 이메일 중복 불가능
    비밀번호 이중 확인
    '''
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.error, status=400)
