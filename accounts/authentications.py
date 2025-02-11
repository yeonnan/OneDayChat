from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # 쿠키에서 access_token 찾기
        access_token = request.COOKIES.get('access_token')
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                if user is None:
                    raise exceptions.AuthenticationFailed('no such user')
                return (user, validated_token)
            except exceptions.AuthenticationFailed:
                pass        # 쿠키 토큰 유효하지 않으면 뒤로 넘어감

        # 쿠키에 없으면 원래 로직 (헤더 authorization) 시도
        return super().authenticate(request)