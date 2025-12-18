"""Structured logging setup. No print statements in production."""

import logging


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s - %(funcName)s - %(lineno)d - %(message)s"
        ),
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module."""
    return logging.getLogger(name)
