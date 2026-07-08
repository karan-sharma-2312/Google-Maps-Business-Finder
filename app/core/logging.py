"""Centralized logging configuration for the application.

This module configures Loguru as the primary logger and intercepts standard
library logging so third-party logs use the same output pipeline.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from app.config.settings import LoggingSettings, PathSettings, get_settings


class InterceptHandler(logging.Handler):
    """Forward standard logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a standard logging record through Loguru.

        The method preserves the original log level and exception info.
        """
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _ensure_log_directory(path_settings: PathSettings) -> None:
    """Create runtime log directory if it does not exist."""
    path_settings.log_dir.mkdir(parents=True, exist_ok=True)


def _build_console_format() -> str:
    """Return human-friendly console format for local development."""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )


def _build_file_format() -> str:
    """Return structured file format compatible with JSON-like parsing."""
    return (
        "{{\"time\": \"{time:YYYY-MM-DDTHH:mm:ss.SSSZ}\", "
        "\"level\": \"{level}\", "
        "\"module\": \"{name}\", "
        "\"function\": \"{function}\", "
        "\"line\": {line}, "
        "\"message\": \"{message}\"}}"
    )


def configure_logging(
    logging_settings: LoggingSettings | None = None,
    path_settings: PathSettings | None = None,
) -> None:
    """Configure global logging sinks and standard logging interception.

    Args:
        logging_settings: Optional explicit logging settings. If not provided,
            settings are loaded from environment.
        path_settings: Optional explicit path settings. If not provided,
            settings are loaded from environment.
    """
    settings = get_settings()
    logging_settings = logging_settings or settings.logging
    path_settings = path_settings or settings.paths

    _ensure_log_directory(path_settings)

    log_file_path: Path = logging_settings.file
    if not log_file_path.is_absolute():
        log_file_path = Path.cwd() / log_file_path

    logger.remove()

    logger.add(
        sys.stdout,
        level=logging_settings.level.upper(),
        format=_build_console_format(),
        backtrace=False,
        diagnose=False,
        enqueue=True,
        colorize=True,
    )

    logger.add(
        log_file_path,
        level=logging_settings.level.upper(),
        format=_build_file_format(),
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        backtrace=False,
        diagnose=False,
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.NOTSET, force=True)

    # Route common library loggers through the intercept handler.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "sqlalchemy"):
        std_logger = logging.getLogger(logger_name)
        std_logger.handlers = [InterceptHandler()]
        std_logger.propagate = False


def get_logger(extra: dict[str, Any] | None = None):
    """Return application logger with optional contextual fields.

    Args:
        extra: Optional key/value context injected into subsequent log lines.

    Returns:
        A bound Loguru logger instance.
    """
    if not extra:
        return logger
    return logger.bind(**extra)
