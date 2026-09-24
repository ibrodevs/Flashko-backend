from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
            if raw_token is not None:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
        return None

def set_refresh_cookie(response, refresh_token):
    max_age = 7 * 24 * 60 * 60  # 7 days
    response.set_cookie(
        key=getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token'),
        value=str(refresh_token),
        max_age=max_age,
        httponly=getattr(settings, 'JWT_AUTH_COOKIE_HTTP_ONLY', True),
        secure=getattr(settings, 'JWT_AUTH_COOKIE_SECURE', False),
        samesite=getattr(settings, 'JWT_AUTH_COOKIE_SAMESITE', 'Lax'),
        path=getattr(settings, 'JWT_AUTH_COOKIE_PATH', '/'),
    )

def delete_refresh_cookie(response):
    response.delete_cookie(
        key=getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', 'refresh_token'),
        path=getattr(settings, 'JWT_AUTH_COOKIE_PATH', '/'),
        samesite=getattr(settings, 'JWT_AUTH_COOKIE_SAMESITE', 'Lax'),
    )
