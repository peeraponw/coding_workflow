"""Shared exceptions for bmad-auto.

Domain-specific exceptions with a clear hierarchy.
"""


class BmadAutoError(Exception):
    """Base exception for all bmad-auto errors."""

    pass


class ConfigError(BmadAutoError):
    """Raised when configuration is invalid or missing."""

    pass


class StateCorruptionError(BmadAutoError):
    """Raised when workflow state file is corrupted or invalid."""

    pass


class AgentError(BmadAutoError):
    """Raised when an agent operation fails."""

    pass


class WorkflowPausedError(BmadAutoError):
    """Raised when workflow is paused (e.g., rate limit, user input needed)."""

    pass
