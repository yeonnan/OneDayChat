from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class SignupAPIView(APIView):
    # 회원가입
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # 로그아웃
    # refresh token 블랙리스트 처리
    def post(self, request):
        try:
            # refresh_token = request.data['refresh_token']     # KeyError 발생
            refresh_token = request.data.get('refresh_token')       # None 반환
            
            # refresh token이 없을 경우 처리
            if not refresh_token:
                return Response({'error' : 'refresh token이 없습니다.'}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message' : '로그아웃 성공'}, status=200)
        except Exception as e:
            return Response({f'로그아웃에 실패하였습니다. : {e}'}, status=400)