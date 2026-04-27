"""
Structured logging for Ghost Mouse.

Uses structlog for structured, contextual logging.
Output: pretty console format for development, JSON for production.
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.config.settings import get_settings


def setup_logging() -> None:
    """Configure structured logging based on settings."""
    settings = get_settings()

    # Choose renderer based on format
    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer(ensure_ascii=False)
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None, **initial_context) -> structlog.BoundLogger:
    """
    Get a structured logger with optional initial context.

    Usage:
        log = get_logger("normalizer", batch_id="B001")
        log.info("normalized_lead", lead_id="abc", field="city")
    """
    logger = structlog.get_logger(name)
    if initial_context:
        logger = logger.bind(**initial_context)
    return logger
