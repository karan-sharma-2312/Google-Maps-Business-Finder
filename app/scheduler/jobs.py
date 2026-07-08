"""Scheduler job definitions."""

from __future__ import annotations

from app.core import get_logger
from app.tasks.celery_app import celery_app

logger = get_logger({"component": "scheduler"})


@celery_app.task(name="jobs.daily_health_check")
def daily_health_check() -> str:
    """Simple scheduled task placeholder for periodic health checks."""
    logger.info("Running daily health check task")
    return "ok"


@celery_app.task(name="jobs.weekly_cleanup")
def weekly_cleanup() -> str:
    """Simple scheduled task placeholder for cleanup workflows."""
    logger.info("Running weekly cleanup task")
    return "cleaned"
