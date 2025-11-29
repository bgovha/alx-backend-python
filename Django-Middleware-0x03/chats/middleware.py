#!/usr/bin/env python3
"""Custom middleware for chats: logging, time restrictions, rate limiting and role checks.

This module contains several middleware classes used by the chat application to
demonstrate middleware responsibilities like logging, request rate limiting and
access control based on user role and time-of-day.
"""
from datetime import datetime, timedelta
import logging
import threading

from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

# Basic logger that writes to chats/requests.log
logger = logging.getLogger("chats.middleware")
handler = logging.FileHandler("chats/requests.log")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log incoming requests with timestamp, user and request path.

    The middleware writes a simple line to `chats/requests.log` for every
    request processed. It is intentionally light-weight to avoid adding
    heavy processing to the request path.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        user_repr = getattr(user, "email", None) or getattr(user, "username", None) or "Anonymous"
        logger.info(f"{datetime.now()} - User: {user_repr} - Path: {request.path}")
        return self.get_response(request)


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """Restrict access to the chat during certain hours.

    Requests that arrive outside the allowed window (06:00-21:59) will be
    rejected with a 403 Forbidden. This prevents access during late-night
    windows according to project requirements.
    """

    def __init__(self, get_response=None, start_hour: int = 6, end_hour: int = 21):
        self.get_response = get_response
        self.start_hour = start_hour
        self.end_hour = end_hour

    def __call__(self, request):
        now = datetime.now()
        if now.hour < self.start_hour or now.hour > self.end_hour:
            # outside 6:00 - 21:59
            return HttpResponseForbidden(
                "Chat service unavailable at this hour. Please try during allowed hours."
            )
        return self.get_response(request)


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """Rate-limit POST messages per IP to avoid abuse.

    This middleware keeps an in-memory sliding window counter of POST
    requests (treated as chat messages) by IP address and denies requests
    that exceed `limit` per `window_seconds`.

    Note:
    - This in-memory approach is suited for a single-process dev server.
      In production use a shared store like Redis.
    """

    _lock = threading.Lock()
    _store = {}

    def __init__(self, get_response=None, limit: int = 5, window_seconds: int = 60):
        self.get_response = get_response
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)

    def _cleanup(self, entries, now):
        # Remove timestamps older than window
        return [t for t in entries if now - t <= self.window]

    def __call__(self, request):
        # We only count POST requests (messages)
        if request.method == "POST":
            ip = request.META.get("REMOTE_ADDR", "unknown")
            now = datetime.now()
            with self._lock:
                entries = self._store.get(ip, [])
                entries = self._cleanup(entries, now)
                if len(entries) >= self.limit:
                    return HttpResponseForbidden(
                        "Rate limit exceeded: too many messages in a short time."
                    )
                entries.append(now)
                self._store[ip] = entries

        return self.get_response(request)


class RolePermissionMiddleware(MiddlewareMixin):
    """Ensure only users with allowed roles can access restricted actions.

    This middleware checks `request.user.role`. If the user is not in the
    allowed roles for a potentially sensitive request (e.g. methods like
    DELETE/PUT or paths containing '/manage' or '/admin'), a 403 is returned.
    """

    def __init__(self, get_response=None, allowed_roles=None):
        self.get_response = get_response
        self.allowed_roles = set(allowed_roles or ["admin", "moderator"])

    def __call__(self, request):
        sensitive_methods = {"PUT", "DELETE", "PATCH"}
        is_sensitive_method = request.method in sensitive_methods
        is_sensitive_path = "/manage" in request.path or "/admin" in request.path

        if is_sensitive_method or is_sensitive_path:
            user = getattr(request, "user", None)
            role = getattr(user, "role", None)
            if role not in self.allowed_roles:
                return HttpResponseForbidden("Insufficient role to perform this action.")

        return self.get_response(request)
