import pyotp
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, mixins, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from security.models import SecurityEvent
from .authentication_helpers import request_ip, friendly_device_name
from .models import User, UserProfile, UserSession
from .serializers import (
    MeSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    UserProfileSerializer,
    SessionSerializer,
)

UserModel = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user.is_online = True
        user.last_active = timezone.now()
        user.save(update_fields=["is_online", "last_active"])

        refresh = RefreshToken.for_user(user)
        SecurityEvent.objects.create(user=user, event_type="ACCOUNT_REGISTERED", ip_address=request_ip(request))

        ua = request.META.get("HTTP_USER_AGENT", "")[:512]
        UserSession.objects.create(
            user=user,
            token_id=str(refresh["jti"]),
            user_agent=ua,
            ip_address=request_ip(request),
            device_name=friendly_device_name(ua),
            is_current=True,
        )

        return Response(
            {
                "user": MeSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/auth/login"""

    serializer_class = TokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        # Optional TOTP pre-check happens via /api/auth/2fa/verify on separate step.
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and "access" in response.data:
            from rest_framework_simplejwt.exceptions import TokenBackendError
            from rest_framework_simplejwt.backends import TokenBackend

            # Decode to get the jti and user
            tb = TokenBackend(algorithm="HS256", signing_key=settings.SECRET_KEY, verifying_key=settings.SECRET_KEY)
            try:
                data = tb.decode(response.data["access"], verify=True)
                user = UserModel.objects.filter(id=data["user_id"], is_active=True).first()
                if user:
                    user.is_online = True
                    user.last_active = timezone.now()
                    user.save(update_fields=["is_online", "last_active"])
                    ua = request.META.get("HTTP_USER_AGENT", "")[:512]
                    UserSession.objects.filter(user=user, is_current=True).update(is_current=False)
                    UserSession.objects.create(
                        user=user,
                        token_id=data.get("jti", ""),
                        user_agent=ua,
                        ip_address=request_ip(request),
                        device_name=friendly_device_name(ua),
                        is_current=True,
                    )
                    SecurityEvent.objects.create(user=user, event_type="LOGIN_SUCCESS", ip_address=request_ip(request), user_agent=ua)
            except Exception:
                pass
        return response


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/me"""

    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveAPIView):
    """GET /api/users/{username}"""

    serializer_class = UserProfileSerializer
    lookup_field = "user__username"
    lookup_url_kwarg = "username"
    queryset = UserProfile.objects.select_related("user").all()

    def get_object(self):
        profile = super().get_object()
        user = profile.user
        if user.profile_visibility == "private" and user != self.request.user:
            self.permission_denied(self.request, "PRIVATE_PROFILE")
        return profile


class LogoutView(generics.GenericAPIView):
    """POST /api/auth/logout — blacklist the refresh token."""

    def post(self, request):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken(request.data.get("refresh"))
            refresh.blacklist()
            user = request.user
            user.is_online = False
            user.save(update_fields=["is_online"])
            SecurityEvent.objects.create(user=user, event_type="LOGOUT", ip_address=request_ip(request))
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "INVALID_PASSWORD"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        SecurityEvent.objects.create(user=user, event_type="PASSWORD_CHANGED", ip_address=request_ip(request))
        return Response({"detail": "PASSWORD_UPDATED"}, status=status.HTTP_200_OK)


class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user


class TOTPSetupView(generics.GenericAPIView):
    """POST /api/auth/2fa/setup -> returns secret; then verify with code."""

    def post(self, request):
        user = request.user
        if user.is_2fa_enabled:
            return Response({"detail": "2FA_ALREADY_ENABLED"}, status=status.HTTP_400_BAD_REQUEST)
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        user.save(update_fields=["two_factor_secret"])
        totp = pyotp.TOTP(secret)
        return Response(
            {
                "secret": secret,
                "provisioning_uri": totp.provisioning_uri(name=user.username, issuer_name="BlackNet"),
            }
        )


class TOTPVerifyView(generics.GenericAPIView):
    """POST /api/auth/2fa/verify { code } -> enable 2FA."""

    def post(self, request):
        from .serializers import TOTPVerifySerializer

        serializer = TOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.two_factor_secret:
            return Response({"detail": "NO_PENDING_SETUP"}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(serializer.validated_data["code"]):
            return Response({"detail": "INVALID_CODE"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_2fa_enabled = True
        user.save(update_fields=["is_2fa_enabled"])
        SecurityEvent.objects.create(user=user, event_type="2FA_ENABLED", ip_address=request_ip(request))
        return Response({"detail": "2FA_ENABLED"})


class TOTPDisableView(generics.GenericAPIView):
    """POST /api/auth/2fa/disable { code }."""

    def post(self, request):
        from .serializers import TOTPVerifySerializer

        serializer = TOTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        totp = pyotp.TOTP(user.two_factor_secret)
        if not totp.verify(serializer.validated_data["code"]):
            return Response({"detail": "INVALID_CODE"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_2fa_enabled = False
        user.two_factor_secret = ""
        user.save(update_fields=["is_2fa_enabled", "two_factor_secret"])
        SecurityEvent.objects.create(user=user, event_type="2FA_DISABLED", ip_address=request_ip(request))
        return Response({"detail": "2FA_DISABLED"})


class SessionsView(generics.ListAPIView):
    """GET /api/users/me/sessions"""

    serializer_class = SessionSerializer

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user).order_by("-last_seen")


class RevokeSessionView(generics.GenericAPIView):
    """POST /api/users/me/sessions/{id}/revoke"""

    def post(self, request, pk):
        session = UserSession.objects.filter(id=pk, user=request.user).first()
        if not session:
            return Response({"detail": "NOT_FOUND"}, status=status.HTTP_404_NOT_FOUND)
        session.revoked_at = timezone.now()
        session.is_current = False
        session.save(update_fields=["revoked_at", "is_current"])
        SecurityEvent.objects.create(user=request.user, event_type="SESSION_REVOKED", ip_address=request_ip(request))
        return Response({"detail": "SESSION_REVOKED"})


class UserListView(generics.ListAPIView):
    """GET /api/users?search= — simple user search."""

    serializer_class = UserSerializer
    search_fields = ["username", "email", "profile__display_name"]

    def get_queryset(self):
        return UserModel.objects.filter(is_active=True, profile_visibility="public").select_related("profile")