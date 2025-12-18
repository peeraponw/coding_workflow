"""Logging configuration using structlog."""

from __future__ import annotations

import logging
from typing import Any

import structlog

DEFAULT_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s"
)


def configure_logging(debug: bool = False, json_output: bool | None = None) -> None:
    """Configure standard logging and structlog."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format=DEFAULT_FORMAT, level=log_level, force=True)
    logging.getLogger().setLevel(log_level)

    processors: list[Any] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        cache_logger_on_first_use=True,
    )
