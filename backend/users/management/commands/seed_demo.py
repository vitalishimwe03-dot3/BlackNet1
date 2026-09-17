"""Seed demo data so the platform is usable immediately after setup.

Creates:
- An admin account
- Demo users with profiles
- Communities + channels
- Posts and comments
- A DM conversation + messages
- Notifications
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

PASS = "BlackNet-Demo-2026"


class Command(BaseCommand):
    help = "Seed BlackNet with demo data for development."

    def handle(self, *args, **options):
        if User.objects.filter(username="admin").exists():
            self.stdout.write("Seed already present. Skipping.")
            return

        from users.models import UserProfile
        from communities.models import Community, CommunityMember, CommunityChannel
        from posts.models import Post, Comment, Like
        from messaging.models import Conversation, ConversationMember, Message
        from notifications.models import Notification

        admin = User.objects.create_superuser("admin", "admin@blacknet.dev", PASS)
        UserProfile.objects.get_or_create(user=admin, defaults={"display_name": "NEXUS ADMIN", "bio": "Platform administrator."})

        demo_users = []
        for idx, (uname, display) in enumerate([
            ("vector", "Vector"),
            ("r3dqueen", "R3D QUEEN"),
            ("k0de", "K0DE"),
            ("sh1bumi", "Sh1bumi"),
            ("ciphergrl", "Cipher"),
        ]):
            user = User.objects.create_user(uname, f"{uname}@blacknet.dev", PASS)
            UserProfile.objects.get_or_create(user=user, defaults={"display_name": display, "bio": f"Welcome to Nexus, {display}."})
            demo_users.append(user)

        net = User.objects.create_user("netmonk", "netmonk@blacknet.dev", PASS)
        UserProfile.objects.get_or_create(user=net, defaults={"display_name": "NET MONK", "bio": "I run the feeds."})

        # Communities
        names = ["development", "linux", "cybersecurity", "ai", "design", "gaming", "science"]
        communities = []
        for slug in names:
            community = Community.objects.create(
                name=slug.capitalize(),
                slug=slug,
                description=f"A community for {slug} enthusiasts.",
                owner=admin,
            )
            CommunityMember.objects.create(community=community, user=admin, role="owner")
            for member in demo_users[:3]:
                CommunityMember.objects.get_or_create(community=community, user=member)
            CommunityChannel.objects.create(community=community, name="general", description="General discussion")
            CommunityChannel.objects.create(community=community, name="showcase", description="Show your work")
            communities.append(community)

        # Posts
        sample_texts = [
            "ACCESS GRANTED :: The relay is stable.",
            "Pushing a new build tonight. Watch the feed.",
            "Tip: use monospace for logs, sans for docs.",
            "Storage system online. Quotas enforced.",
            "Community channels are live.",
            "Anyone testing the new API?",
        ]
        for i, text in enumerate(sample_texts):
            Post.objects.create(
                author=demo_users[i % len(demo_users)],
                content=text,
                post_type="text",
                community=communities[i % len(communities)],
            )

        # Comments follow the first post
        first_post = Post.objects.filter(content__icontains="relay").first()
        if first_post:
            Comment.objects.create(post=first_post, author=demo_users[1], content="Linking up now.")
            Comment.objects.create(post=first_post, author=demo_users[2], content="Confirmed on my end.")

        # DM conversation
        conv = Conversation.objects.create(type="private", partner=demo_users[1], created_by=demo_users[0])
        ConversationMember.objects.create(conversation=conv, user=demo_users[0])
        ConversationMember.objects.create(conversation=conv, user=demo_users[1])
        Message.objects.create(conversation=conv, sender=demo_users[0], content="Hey, check the new vault.")
        Message.objects.create(conversation=conv, sender=demo_users[1], content="Nice, keys are safe.")

        group_conv = Conversation.objects.create(type="group", name="++ DEV TEAM ++", created_by=demo_users[0])
        for u in demo_users[:4]:
            ConversationMember.objects.create(conversation=group_conv, user=u)
        Message.objects.create(conversation=group_conv, sender=demo_users[0], content="Route secured, ship it.")

        # Notifications
        for u in demo_users[:2]:
            Notification.objects.create(
                recipient=u,
                actor=admin,
                kind="system",
                message="NEXUS READY // WELCOME",
            )

        self.stdout.write(self.style.SUCCESS("Seed data created."))
        self.stdout.write(f"Admin login: admin / {PASS}")