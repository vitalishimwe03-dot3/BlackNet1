"""Integration/unit tests for BlackNet.

Covers: auth, permissions, file quotas/accounting, uploads, posts & comments,
messaging, notifications, communities, share links, and security controls.
"""
import io
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from communities.models import Community, CommunityMember
from files.models import File, Folder, ShareLink, StorageUsage
from messaging.models import Conversation, ConversationMember, Message
from notifications.models import Notification
from posts.models import Post, Like, Comment
from users.models import UserProfile

User = get_user_model()


def auth_headers(user):
    refresh = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}"}


def make_user(username, password="Str0ng!Passw0rd"):
    user = User.objects.create_user(username, f"{username}@blacknet.dev", password)
    UserProfile.objects.get_or_create(user=user)
    return user


class AuthTests(APITestCase):
    def test_register_then_login(self):
        resp = self.client.post(
            reverse("auth_register"),
            {"username": "nova", "email": "nova@blacknet.dev", "password": "Str0ng!Passw0rd"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

        user = User.objects.get(username="nova")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.storage_bytes_total, 5 * 1024**3)

        resp = self.client.post(
            reverse("auth_login"),
            {"username": "nova", "password": "Str0ng!Passw0rd"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_login_bad_credentials(self):
        resp = self.client.post(reverse("auth_login"), {"username": "nova", "password": "wrong"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_flow(self):
        make_user("jane")
        login = self.client.post(reverse("auth_login"), {"username": "jane", "password": "Str0ng!Passw0rd"})
        refresh = login.data["refresh"]
        resp = self.client.post(reverse("auth_refresh"), {"refresh": refresh})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_logout_blacklists_token(self):
        user = make_user("jane")
        refresh = RefreshToken.for_user(user)
        resp = self.client.post(reverse("auth_logout"), {"refresh": str(refresh)}, **auth_headers(user))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_protected_endpoint_requires_auth(self):
        resp = self.client.get(reverse("users_me"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(APITestCase):
    def setUp(self):
        self.a = make_user("alice")
        self.b = make_user("bob")

    def test_private_profile_blocked(self):
        self.b.profile_visibility = "private"
        self.b.save()
        resp = self.client.get(reverse("users_detail", args=["bob"]), **auth_headers(self.a))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_edit_own_profile_only(self):
        resp = self.client.patch(
            reverse("users_me_profile"),
            {"display_name": "ALICE-7"},
            format="json",
            **auth_headers(self.a),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class StorageQuotaTests(APITestCase):
    def setUp(self):
        self.user = make_user("storage1")
        self.headers = auth_headers(self.user)

    def upload(self, name="hello.txt", content=b"hello world", extra=None):
        payload = {"file": SimpleUploadedFile(name, content)}
        if extra:
            payload.update(extra)
        return self.client.post(reverse("files-upload"), payload, format="multipart", **self.headers)

    def test_upload_updates_usage(self):
        resp = self.upload()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.storage_bytes_used, 11)
        usage = StorageUsage.objects.get(user=self.user)
        self.assertEqual(usage.file_count, 1)
        self.assertEqual(usage.used_bytes, 11)

    def test_quota_rejected_when_exceeded(self):
        user = self.user
        user.storage_bytes_total = 5  # bytes
        user.storage_bytes_used = 5
        user.save()
        resp = self.upload()
        self.assertEqual(resp.status_code, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    def test_delete_recomputes_usage(self):
        resp = self.upload()
        file_id = resp.data["id"]
        self.client.delete(reverse("files-detail", args=[file_id]), **self.headers)
        self.user.refresh_from_db()
        self.assertEqual(self.user.storage_bytes_used, 0)

    def test_executable_blocked(self):
        content = b"\x4d\x5atest executable payload"
        resp = self.upload(name="evil.exe", content=content)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rename_and_move(self):
        resp = self.upload()
        file_id = resp.data["id"]
        r2 = self.client.post(reverse("files-rename", args=[file_id]), {"name": "renamed.txt"}, **self.headers)
        self.assertEqual(r2.status_code, status.HTTP_200_OK)
        self.assertEqual(r2.data["original_name"], "renamed.txt")

        folder = Folder.objects.create(owner=self.user, name="docs")
        r3 = self.client.post(reverse("files-move", args=[file_id]), {"folder": str(folder.pk)}, **self.headers)
        self.assertEqual(r3.status_code, status.HTTP_200_OK)
        self.assertEqual(r3.data["folder"], str(folder.pk))

    def test_cannot_access_other_users_file(self):
        other = make_user("otheruser")
        resp = self.upload()
        file_id = resp.data["id"]
        r = self.client.get(reverse("files-detail", args=[file_id]), **auth_headers(other))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class PostCommentTests(APITestCase):
    def setUp(self):
        self.a = make_user("poster")
        self.b = make_user("reader")

    def test_create_post_and_like_comment(self):
        post = Post.objects.create(author=self.a, content="hello nexus")
        resp = self.client.post(reverse("posts-like", args=[post.pk]), **auth_headers(self.b))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["liked"])
        self.assertEqual(Like.objects.filter(post=post).count(), 1)

        resp = self.client.post(reverse("posts-comments", args=[post.pk]), {"content": "nice"}, **auth_headers(self.b))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.filter(post=post).count(), 1)

        # recipient notified
        self.assertTrue(Notification.objects.filter(recipient=self.a).exists())


class MessagingTests(APITestCase):
    def setUp(self):
        self.a = make_user("msga")
        self.b = make_user("msgb")

    def test_direct_conversation_and_send(self):
        resp = self.client.post(reverse("conversations-direct"), {"username": "msgb"}, **auth_headers(self.a))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        conv_id = resp.data["id"]
        send_url = reverse("message_send", args=[conv_id])
        r = self.client.post(send_url, {"content": "hello bob"}, **auth_headers(self.a))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.filter(conversation_id=conv_id).count(), 1)

    def test_send_to_conversation_not_member_forbidden(self):
        c = Conversation.objects.create(type="private", created_by=self.a, partner=self.b)
        ConversationMember.objects.create(conversation=c, user=self.a)
        send_url = reverse("message_send", args=[c.pk])
        r = self.client.post(send_url, {"content": "spam"}, **auth_headers(make_user("intruder")))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class NotificationTests(APITestCase):
    def setUp(self):
        self.a = make_user("notifa")

    def test_list_and_mark_read(self):
        Notification.objects.create(recipient=self.a, kind="system", message="TEST")
        resp = self.client.get(reverse("notifications-list"), **auth_headers(self.a))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        nid = resp.data["results"][0]["id"]
        r = self.client.patch(reverse("notifications-detail", args=[nid]), {"is_read": True}, **auth_headers(self.a))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.client.post(reverse("notifications_read_all"), **auth_headers(self.a))


class CommunityTests(APITestCase):
    def setUp(self):
        self.a = make_user("comma")
        self.b = make_user("commb")

    def test_create_join_leave(self):
        resp = self.client.post(
            reverse("communities-list"),
            {"name": "Sailors", "slug": "sailors", "description": "A safe community"},
            **auth_headers(self.a),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cid = resp.data["id"]

        r = self.client.post(reverse("communities-join", args=[cid]), **auth_headers(self.b))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data["joined"])


class ShareLinkTests(APITestCase):
    def setUp(self):
        self.a = make_user("sharea")
        self.headers = auth_headers(self.a)

    def test_create_and_expire_link(self):
        f = File.objects.create(
            owner=self.a,
            original_name="doc.txt",
            stored_name="uploads/x.txt",
            size_bytes=5,
        )
        resp = self.client.post(reverse("files_share", args=[f.pk]), {}, **self.headers)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        token = resp.data["token"]

        link = ShareLink.objects.get(token=token)
        self.assertTrue(link.can_download())
        link.expires_at = timezone.now() - timezone.timedelta(hours=1)
        link.save()
        self.assertFalse(link.can_download())


class SecurityEventTests(APITestCase):
    def test_overview_and_sessions(self):
        from security.models import SecurityEvent
        a = make_user("seca")
        SecurityEvent.objects.create(user=a, event_type="LOGIN_SUCCESS")
        resp = self.client.get(reverse("security_overview"), **auth_headers(a))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("two_factor_enabled", resp.data)


class WebsocketAuthTests(TestCase):
    """Ensure unauthenticated WebSocket connections are refused."""

    def test_consumer_requires_token(self):
        from channels.testing import WebsocketCommunicator
        from messaging.consumers import ConversationConsumer

        communicator = WebsocketCommunicator(
            ConversationConsumer.as_asgi(),
            f"/ws/conversations/{uuid.uuid4()}/",
        )
        connected, _ = communicator.connect()
        self.assertFalse(connected)
        communicator.disconnect()