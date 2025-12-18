"""Exception hierarchy for bmad-auto."""


class BmadAutoError(Exception):
    """Base exception for all bmad-auto errors."""


class ConfigurationError(BmadAutoError):
    """Raised when configuration is invalid or missing."""


class AgentNotFoundError(BmadAutoError):
    """Raised when a CLI agent binary cannot be located."""


class AgentExecutionError(BmadAutoError):
    """Raised when a CLI agent returns a non-zero exit code."""


class AgentTimeoutError(BmadAutoError):
    """Raised when an agent subprocess exceeds its timeout."""


class AgentOutputParseError(BmadAutoError):
    """Raised when parsing agent output fails."""


class WorkflowError(BmadAutoError):
    """Base class for workflow-level failures."""


class EpicNotFoundError(WorkflowError):
    """Raised when an epic file cannot be found."""


class StoryCreationError(WorkflowError):
    """Raised when story creation fails."""


class ReviewRejectedError(WorkflowError):
    """Raised when review repeatedly rejects a story implementation."""


class GitOperationError(BmadAutoError):
    """Raised when git operations fail."""


class StateError(BmadAutoError):
    """Raised when state persistence fails."""
