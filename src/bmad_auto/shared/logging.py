"""Logging utilities for bmad-auto.

Provides structlog configuration for machine-parseable logs and Rich console
for human-readable output.

Per project-context.md:
- Use structlog for logging (debugging/auditing)
- Use Rich console for display (user-facing output)
- NEVER use print() for output
"""

from rich.console import Console

import structlog
from structlog.typing import EventDict

# Color constants for agent phases
SM_COLOR = "blue"
DEV_COLOR = "green"
REVIEWER_COLOR = "yellow"

# Shared console instance for user-facing output
console = Console()


def _add_timestamp(
    logger: object,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add ISO timestamp to log entries."""
    from datetime import datetime

    event_dict["timestamp"] = datetime.now().isoformat()
    return event_dict


# Configure structlog with timestamp processor
structlog.configure(
    processors=[
        _add_timestamp,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structlog logger with the given name.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        A configured structlog BoundLogger instance.
    """
    return structlog.get_logger(name)


def print_sm(message: str) -> None:
    """Print message with SM (blue) color prefix.

    Args:
        message: The message to print.
    """
    console.print(f"[{SM_COLOR}]SM:[/{SM_COLOR}] {message}")


def print_dev(message: str) -> None:
    """Print message with Dev (green) color prefix.

    Args:
        message: The message to print.
    """
    console.print(f"[{DEV_COLOR}]Dev:[/{DEV_COLOR}] {message}")


def print_reviewer(message: str) -> None:
    """Print message with Reviewer (yellow) color prefix.

    Args:
        message: The message to print.
    """
    console.print(f"[{REVIEWER_COLOR}]Reviewer:[/{REVIEWER_COLOR}] {message}")
