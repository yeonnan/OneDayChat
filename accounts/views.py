from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.serializers import UserSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password


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
            refresh_token = request.data.get("refresh_token")  # None 반환

            # refresh token이 없을 경우 처리
            if not refresh_token:
                return Response({"error": "refresh token이 없습니다."}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃 성공"}, status=200)
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
