#!/usr/bin/env python3
"""App configuration for the messaging app.

It ensures signals are registered when the app is ready.
"""
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """Configuration for the messaging app that registers signals on ready."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self) -> None:
        # Import receivers to register signals
        from . import signals  # noqa: F401
