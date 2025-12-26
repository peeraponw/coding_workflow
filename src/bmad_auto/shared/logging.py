"""Logging utilities for bmad-auto.

Provides structlog configuration for machine-parseable logs and Rich console
for human-readable output.

Per project-context.md:
- Use structlog for logging (debugging/auditing)
- Use Rich console for display (user-facing output)
- NEVER use print() for output
"""

import re
from datetime import datetime

from rich.console import Console

import structlog
from structlog.typing import EventDict
from typing import Final

# Agent color constants for workflow logging
AGENT_COLORS: Final[dict[str, str]] = {
    "WORKFLOW": "cyan",
    "SM": "blue",
    "DEV": "green",
    "REVIEWER": "yellow",
    "ERROR": "red",
    "GIT": "magenta",
}

# Legacy color constants (for backward compatibility)
SM_COLOR: Final[str] = AGENT_COLORS["SM"]
DEV_COLOR: Final[str] = AGENT_COLORS["DEV"]
REVIEWER_COLOR: Final[str] = AGENT_COLORS["REVIEWER"]

# Shared console instance for user-facing output
console = Console()

# Sensitive data patterns for sanitization (NFR14)
SENSITIVE_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"ANTHROPIC_API_KEY=\S+", re.IGNORECASE),
    re.compile(r"api[_-]?key[=:]\S+", re.IGNORECASE),
    re.compile(r"token[=:]\S+", re.IGNORECASE),
    re.compile(r"bearer \S+", re.IGNORECASE),
    re.compile(r"password[=:]\S+", re.IGNORECASE),
)


def _add_timestamp(
    logger: object,
    method_name: str,
    event_dict: EventDict,
) -> EventDict:
    """Add ISO timestamp to log entries."""
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


def sanitize_log(message: str) -> str:
    """Remove sensitive data from log messages (NFR14).

    Args:
        message: The message to sanitize.

    Returns:
        The message with sensitive data redacted.
    """
    for pattern in SENSITIVE_PATTERNS:
        message = pattern.sub("[REDACTED]", message)
    return message


def log_phase(agent: str, message: str) -> None:
    """Log phase event with timestamp and color.

    Args:
        agent: Agent name (WORKFLOW, SM, DEV, REVIEWER, GIT, ERROR).
        message: The message to log.

    Displays format: [timestamp] AGENT: message
    """
    timestamp = datetime.now().isoformat(timespec="seconds")
    color = AGENT_COLORS.get(agent, "white")
    sanitized = sanitize_log(message)

    console.print(
        f"[dim][{timestamp}][/dim] [{color}]{agent}:[/{color}] {sanitized}"
    )


def log_workflow_start(epic_path: str) -> None:
    """Log workflow start event.

    Args:
        epic_path: Path to the epic file.
    """
    log_phase("WORKFLOW", f"Starting epic {epic_path}")


def log_phase_start(phase: str, story_num: int, total: int) -> None:
    """Log phase start event.

    Args:
        phase: Phase name (SM, DEV, REVIEWER).
        story_num: Current story number.
        total: Total number of stories.
    """
    log_phase(phase, f"Creating story {story_num} of {total}...")


def log_phase_complete(phase: str, details: str) -> None:
    """Log phase complete event.

    Args:
        phase: Phase name (SM, DEV, REVIEWER).
        details: Details about completion.
    """
    log_phase(phase, details)


def log_story_complete(story_id: str, files_modified: int = 0) -> None:
    """Log story complete event.

    Args:
        story_id: Story identifier.
        files_modified: Number of files modified.
    """
    msg = f"Story complete - {story_id}"
    if files_modified > 0:
        msg += f" ({files_modified} files modified)"
    log_phase("DEV", msg)


def log_error(error_type: str, message: str) -> None:
    """Log error with timestamp and details.

    Args:
        error_type: Type of error (e.g., "rate_limit", "api_error").
        message: Error message.
    """
    timestamp = datetime.now().isoformat(timespec="seconds")
    sanitized = sanitize_log(message)

    console.print(
        f"[dim][{timestamp}][/dim] [red]ERROR:[/red] {error_type}: {sanitized}"
    )


def log_handoff(from_agent: str, to_agent: str, reason: str) -> None:
    """Log agent handoff with reason.

    Args:
        from_agent: Source agent name (SM, DEV, REVIEWER).
        to_agent: Target agent name (SM, DEV, REVIEWER).
        reason: Reason for handoff (should be concise, under 50 chars).
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    from_color = AGENT_COLORS.get(from_agent, "white")
    to_color = AGENT_COLORS.get(to_agent, "white")
    sanitized = sanitize_log(reason)

    console.print(
        f"[dim][{timestamp}][/dim] [cyan]HANDOFF:[/cyan] "
        f"[{from_color}]{from_agent}[/] → "
        f"[{to_color}]{to_agent}[/] "
        f"[dim]({sanitized})[/dim]"
    )

    # Also log to structlog for debugging
    logger = get_logger(__name__)
    logger.info(
        "agent_handoff",
        from_agent=from_agent,
        to_agent=to_agent,
        reason=sanitized,
    )


def log_review_approved() -> None:
    """Log review approval event."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(
        f"[dim][{timestamp}][/dim] [green]REVIEW:[/green] Approved - proceeding to commit"
    )

    # Also log to structlog for debugging
    logger = get_logger(__name__)
    logger.info("review_approved")


# Legacy agent print functions (for backward compatibility)

def print_sm(message: str) -> None:
    """Print message with SM (blue) color prefix.

    Args:
        message: The message to print.
    """
    log_phase("SM", message)


def print_dev(message: str) -> None:
    """Print message with Dev (green) color prefix.

    Args:
        message: The message to print.
    """
    log_phase("DEV", message)


def print_reviewer(message: str) -> None:
    """Print message with Reviewer (yellow) color prefix.

    Args:
        message: The message to print.
    """
    log_phase("REVIEWER", message)
