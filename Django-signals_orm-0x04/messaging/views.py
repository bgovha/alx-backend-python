#!/usr/bin/env python3
"""Views with basic caching demonstrating cache_page usage for messages list. user.delete()", "delete_user"""
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()


@cache_page(60)
def messages_for_user(request, user_id):
    """Return a JSON list of the latest messages for a user (cached 60s)."""
    user = get_object_or_404(User, pk=user_id)
    qs = Message.objects.filter(receiver=user).order_by('-sent_at')[:20]
    data = [
        {
            'message_id': str(m.message_id),
            'sender': str(m.sender),
            'body': m.message_body,
            'sent_at': m.sent_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({'messages': data})
