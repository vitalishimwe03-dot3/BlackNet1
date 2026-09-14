from django.contrib import admin
from .models import Conversation, ConversationMember, Message, Presence


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("type", "name", "created_by", "last_message_at")
    list_filter = ("type",)


@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "conversation", "last_read_at", "is_typing")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "conversation", "is_deleted", "created_at")
    list_filter = ("is_deleted",)


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ("user", "is_online", "last_seen")