#!/usr/bin/env python3
"""Unit tests for messaging app: signals, ORM behavior and caching."""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message, Notification, MessageHistory
from django.urls import reverse


User = get_user_model()


class MessagingSignalsTests(TestCase):
    """Tests for signals and ORM behaviors described in the project."""

    def setUp(self):
        self.u1 = User.objects.create_user(username='u1', password='pwd1', email='u1@example.com')
        self.u2 = User.objects.create_user(username='u2', password='pwd2', email='u2@example.com')

    def test_message_creation_creates_notification(self):
        msg = Message.objects.create(sender=self.u1, receiver=self.u2, message_body='Hello')
        # notification should be created via post_save signal
        notifications = Notification.objects.filter(user=self.u2, message=msg)
        self.assertEqual(notifications.count(), 1)

    def test_edit_message_creates_history_and_marks_edited(self):
        msg = Message.objects.create(sender=self.u1, receiver=self.u2, message_body='Original')
        msg.message_body = 'Updated content'
        msg.save()
        # MessageHistory should have an entry
        history_qs = MessageHistory.objects.filter(message=msg)
        self.assertTrue(history_qs.exists())
        self.assertTrue(Message.objects.get(pk=msg.pk).edited)

    def test_delete_user_cleans_related_data(self):
        m1 = Message.objects.create(sender=self.u1, receiver=self.u2, message_body='M1')
        Notification.objects.create(user=self.u2, message=m1)
        # Delete u2 and assert their messages and notifications are removed
        self.u2.delete()
        self.assertFalse(Message.objects.filter(pk=m1.pk).exists())
        self.assertFalse(Notification.objects.filter(message=m1).exists())


class ORMAdvancedTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username='u1', password='pwd1', email='u1@example.com')
        self.u2 = User.objects.create_user(username='u2', password='pwd2', email='u2@example.com')

    def test_threaded_replies_prefetch(self):
        parent = Message.objects.create(sender=self.u1, receiver=self.u2, message_body='Parent')
        child1 = Message.objects.create(sender=self.u2, receiver=self.u1, message_body='Reply1', parent_message=parent)
        child2 = Message.objects.create(sender=self.u2, receiver=self.u1, message_body='Reply2', parent_message=parent)

        # Use select_related/prefetch_related to load replies efficiently
        qs = Message.objects.filter(pk=parent.pk).prefetch_related('replies')
        obj = qs.first()
        replies = list(obj.replies.all())
        self.assertEqual(len(replies), 2)

    def test_unread_manager_returns_only_unread(self):
        Message.objects.create(sender=self.u1, receiver=self.u2, message_body='R1', read=False)
        Message.objects.create(sender=self.u1, receiver=self.u2, message_body='R2', read=True)
        unread = Message.unread.unread_for(self.u2)
        self.assertEqual(unread.count(), 1)


class CachingViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.u1 = User.objects.create_user(username='u1', password='pwd1', email='u1@example.com')
        self.u2 = User.objects.create_user(username='u2', password='pwd2', email='u2@example.com')

    def test_messages_view_cache(self):
        # Create an initial message
        m1 = Message.objects.create(sender=self.u1, receiver=self.u2, message_body='Hello cache')

        # Directly call the view via URL pattern (it is not included in urls, so call the view function)
        from .views import messages_for_user
        # Since messages_for_user expects request and user id, use test client to hit a temporary URL path
        url = f'/messages/{self.u2.pk}/'

        # Create a simple URL handler in the test using the view callable
        response1 = self.client.get(url)
        # no route exists — still ensure calling view directly works
        # instead call the view manually
        from django.test import RequestFactory
        rf = RequestFactory()
        req = rf.get('/dummy')
        resp1 = messages_for_user(req, user_id=self.u2.pk)
        import json as _json
        content1 = _json.loads(resp1.content.decode())

        # Add another message — but the cached view should still return the old list
        Message.objects.create(sender=self.u1, receiver=self.u2, message_body='Another')
        resp2 = messages_for_user(req, user_id=self.u2.pk)
        content2 = _json.loads(resp2.content.decode())

        self.assertEqual(content1, content2)
