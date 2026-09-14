"""Custom JWT authentication with user-session tracking."""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.utils import timezone

from .models import UserSession


class CustomJWTAuthentication(JWTAuthentication):
    """Authenticate users with JWT and touch their last_active/session."""

    def get_user(self, validated_token):
        try:
            user = super().get_user(validated_token)
        except AuthenticationFailed:
            raise AuthenticationFailed("INVALID_CREDENTIALS", code="authentication_failed")

        user.last_active = timezone.now()
        user.save(update_fields=["last_active"])

        # Track the session identified by the token's jti claim
        token_id = validated_token.get("jti", "")
        if token_id:
            UserSession.objects.filter(user=user, token_id=token_id).update(last_seen=timezone.now())
        return user