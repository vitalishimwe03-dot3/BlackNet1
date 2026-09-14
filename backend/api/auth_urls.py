from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    TOTPSetupView,
    TOTPVerifyView,
    TOTPDisableView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="auth_register"),
    path("login", LoginView.as_view(), name="auth_login"),
    path("refresh", TokenRefreshView.as_view(), name="auth_refresh"),
    path("verify", TokenVerifyView.as_view(), name="auth_verify"),
    path("logout", LogoutView.as_view(), name="auth_logout"),
    path("change-password", ChangePasswordView.as_view(), name="auth_change_password"),
    path("2fa/setup", TOTPSetupView.as_view(), name="auth_2fa_setup"),
    path("2fa/verify", TOTPVerifyView.as_view(), name="auth_2fa_verify"),
    path("2fa/disable", TOTPDisableView.as_view(), name="auth_2fa_disable"),
]