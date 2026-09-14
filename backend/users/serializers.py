import pyotp
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers

from .models import User, UserProfile, UserSession

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public-facing user representation."""

    class Meta:
        model = UserModel
        fields = [
            "id", "username", "avatar", "bio",
            "created_at", "last_active", "is_online",
            "profile_visibility", "reputation_public",
        ]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    story_bio = serializers.CharField(source="bio", read_only=True)

    class Meta:
        model = UserProfile
        fields = ["username", "display_name", "location", "website", "github", "bio", "reputation", "badges"]
        read_only_fields = ["username", "reputation", "badges"]


class MeSerializer(serializers.ModelSerializer):
    """Full detail of the authenticated user."""

    class Meta:
        model = UserModel
        fields = [
            "id", "username", "email", "avatar", "bio",
            "is_email_verified", "last_active", "is_online",
            "is_2fa_enabled", "created_at",
            "storage_bytes_total", "storage_bytes_used",
            "profile_visibility",
            "notify_new_messages", "notify_likes", "notify_comments",
            "notify_followers", "notify_mentions", "notify_community",
            "notify_security", "email_notifications",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = UserModel
        fields = ["id", "username", "email", "password"]

    def validate_password(self, value):
        try:
            validate_password(value)
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, bio=user.bio or "")
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError(exc.messages)
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Privacy + notification settings and profile edits."""

    bio = serializers.CharField(source="profile.bio", required=False, allow_blank=True, max_length=500)
    display_name = serializers.CharField(source="profile.display_name", required=False, allow_blank=True, max_length=64)
    location = serializers.CharField(source="profile.location", required=False, allow_blank=True, max_length=128)
    website = serializers.URLField(source="profile.website", required=False, allow_blank=True)
    github = serializers.CharField(source="profile.github", required=False, allow_blank=True, max_length=64)

    class Meta:
        model = UserModel
        fields = [
            "avatar", "bio", "display_name", "location", "website", "github",
            "profile_visibility", "reputation_public",
            "notify_new_messages", "notify_likes", "notify_comments",
            "notify_followers", "notify_mentions", "notify_community",
            "notify_security", "email_notifications",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        profile = instance.profile
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()
        return instance


class TOTPSetupSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class TOTPVerifySerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = ["id", "user_agent", "ip_address", "device_name", "is_current", "created_at", "last_seen"]


class Enable2FARequestSerializer(serializers.Serializer):
    """Generate a TOTP secret and provisioning URI for a user."""

    def to_representation(self, instance):
        return {
            "secret": instance.totp_secret,
            "provisioning_uri": instance.totp_uri,
            "message": "SCAN WITH AUTHENTICATOR // CONFIRM WITH CODE",
        }


class SecurityEventSerializer(serializers.Serializer):
    pass