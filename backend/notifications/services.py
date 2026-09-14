"""Notification creation + push helper."""

import re

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Notification


def notify(recipient, message, actor=None, kind="system", post=None, message_obj=None, file=None, data=None):
    """Create a Notification row + push a realtime event to the user's group."""
    if not recipient:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        message=message,
        post=post,
        message_obj=message_obj,
        file=file,
        data=data or {},
    )

    try:
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            f"notifications_{recipient.pk}",
            {
                "type": "notification.event",
                "payload": {
                    "id": str(notification.pk),
                    "kind": kind,
                    "message": message,
                    "created_at": timezone.now().isoformat(),
                    "is_read": False,
                },
            },
        )
    except Exception:
        pass
    return notification


def notify_mention(content, actor, post=None, message_obj=None):
    """Parse @mentions and notify each mentioned user (respecting their prefs)."""
    for match in re.finditer(r"@([A-Za-z0-9_]{1,32})", content):
        username = match.group(1).lower()
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.filter(username__iexact=username, is_active=True).first()
        if user and user != actor and user.notify_mentions:
            notify(user, f"YOU WERE MENTIONED BY @{actor.username}", actor=actor, kind="mention", post=post)