"""Notification dispatcher strategies."""

from __future__ import annotations

from typing import Protocol

from app.core import get_logger

logger = get_logger({"component": "notifications"})


class NotificationProvider(Protocol):
    """Interface for notification provider implementations."""

    def send(self, subject: str, message: str) -> None:
        """Send notification payload."""


class LogNotificationProvider:
    """Default provider that logs notifications."""

    def send(self, subject: str, message: str) -> None:
        logger.info("Notification subject='{}' message='{}'", subject, message)


class NotificationDispatcher:
    """Dispatch notifications via configured provider."""

    def __init__(self, provider: NotificationProvider | None = None) -> None:
        self._provider = provider or LogNotificationProvider()

    def notify(self, subject: str, message: str) -> None:
        self._provider.send(subject, message)
