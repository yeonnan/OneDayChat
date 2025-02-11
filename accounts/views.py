from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.serializers import UserSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password


'''
TokenObtainPairView : access + refresh token 토큰 2개를 발급하는 뷰. json으로 토큰을 준다.
TokenRefreshView : 이미 발급된 refresh token을 사용해 새로운 access token 재발급 해주는 뷰
'''



class CookieTokenObtainPairView(TokenObtainPairView):
    # simpleJWT의 TokenObtainPairView를 상속받아 access, refresh 토큰을 response body + httponly 쿠키로 반환
    def post(self, request, *args, **kwargs):
        # 원본 로직 수행
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 유효하면 refresh, access 토큰 꺼내기
        refresh = serializer.validated_data['refresh']
        access = serializer.validated_data['access']

        # 응답 데이터
        response = Response({
            'message' : '로그인 성공',
            'access_token' : str(access),       # 디버깅
            'refresh_token' : str(refresh),     # 디버깅
            }, status=200)

        # HttpOnly 쿠키로 토큰 전달
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=False,
            samesite='None'
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='None'
        )
        return response


class CookieTokenRefreshView(TokenRefreshView):
    # simpleJWT의 TokenRefreshView를 상속받아 쿠키의 refresh token을 사용해 access token 재발급
    def post(self, request, *args, **kwargs):

        # 쿠키에서 refresh token을 꺼내고 싶다면
        refresh_token = request.COOKIES.get('refresh_token', None)

        if not refresh_token:
            refresh_token = request.data.get('refresh', None)
        
        if not refresh_token:
            return Response({'error' : 'refresh token이 없습니다.'}, status=400)
        
        # request.data를 복사해서 refresh 필드에 쿠키로 받은 토큰을 넣어줌
        data = {'refresh':refresh_token}

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error' : f'token 재발급 오류 : {e}'}, status=400)
        
        # 새 access token
        access_token = serializer.validated_data['access']
        response = Response({
            'message' : '토큰이 재발급되었습니다.',
            'access_token' : str(access_token)      # 디버깅
            }, status=200)

        # 재발급된 access token 쿠키에 다시 저장
        response.set_cookie(
            key='access_token',
            value=str(access_token),
            httponly=True,
            secure=False,
            samesite='None'
        )
        return response


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
    # 쿠키에 있는 refresh token 꺼내서 블랙리스트 처리, 쿠키 제거
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token", None) 

            if not refresh_token:
                return Response({"error": "refresh token이 없습니다."}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()

            # 쿠키 제거
            response = Response({"message": "로그아웃 성공"}, status=200)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response

        except Exception as e:
            return Response({f"로그아웃에 실패하였습니다. : {e}"}, status=400)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 비밀번호 변경
    def put(self, request, pk):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "old password와 new password가 필요합니다."}, status=400)

        # 현재 비밀번호 확인
        if not check_password(old_password, request.user.password):
            return Response({"error": "현재 비밀번호가 올바르지 않습니다."}, status=400)

        # 비밀번호 확인
        serializer = ChangePasswordSerializer(data={"password": new_password})
        serializer.is_valid(raise_exception=True)

        # 비밀번호 변경
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "비밀번호가 변경되었습니다."}, status=200)


class DeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 회원탈퇴
    def delete(self, request, pk):
        user = request.user
        password = request.data.get("password")
        if not password or not check_password(password, user.password):
            return Response({"error": "올바른 비밀번호를 입력해주세요."}, status=400)

        user.delete()
        return Response(status=200)
