#!/usr/bin/env python3
"""Models for messaging app: messages, notifications and history.

Includes a custom manager for unread messages and threaded replies support.
"""
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from typing import Any


User = get_user_model()


class UnreadMessagesManager(models.Manager):
    """Manager returning unread messages for a given user."""

    def unread_for(self, user: Any):
        """Return a queryset of unread messages for `user` using only required fields."""
        return self.filter(receiver=user, read=False).only('message_id', 'message_body', 'sent_at')


class Message(models.Model):
    """A chat message between users. Supports threaded replies via parent_message."""

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    objects = models.Manager()
    unread = UnreadMessagesManager()

    def __str__(self) -> str:
        return f"Message {self.message_id} from {self.sender} to {self.receiver}"


class Notification(models.Model):
    """A lightweight notification created when a message is received."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"Notification {self.id} for {self.user} about message {self.message.message_id}"


class MessageHistory(models.Model):
    """Stores historical copies of message content before an edit. timestamp"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"History for {self.message.message_id} at {self.edited_at}"
