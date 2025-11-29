#!/usr/bin/env python3
"""Signal handlers for the messaging app.

Handlers:
- Create Notification on message creation (post_save)
- Save MessageHistory on message edits (pre_save)
- Cleanup related data when a User is deleted (post_delete)
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Message, Notification, MessageHistory

User = get_user_model()


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance: Message, created: bool, **kwargs) -> None:
    """Create a Notification for the receiver when a new Message is created."""
    if created:
        Notification.objects.create(user=instance.receiver, message=instance)


@receiver(pre_save, sender=Message)
def record_message_history_on_edit(sender, instance: Message, **kwargs) -> None:
    """Before saving a message, if the content changed, store the old content."""
    if not instance.pk:
        # new message — no history to record
        return

    try:
        old = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # If changed content, record history
    if old.message_body != instance.message_body:
        MessageHistory.objects.create(message=old, old_content=old.message_body)
        instance.edited = True


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance: User, **kwargs) -> None:
    """When a user is deleted, ensure related messages/notifications/history are cleaned up.

    As model relations use CASCADE this handler is defensive — it can perform
    additional cleanup or logging as needed.
    """
    # Delete messages where user is sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    # Delete notifications related to this user
    Notification.objects.filter(user=instance).delete()
    # MessageHistory linked by message will be removed by cascade when message deletes
