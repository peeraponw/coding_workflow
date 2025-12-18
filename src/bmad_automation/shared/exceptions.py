"""Custom exception hierarchy. No bare Exception usage."""


class BmadError(Exception):
    """Base exception for all BMAD errors."""


class EpicParseError(BmadError):
    """Raised when epic file parsing fails."""


class GitOperationError(BmadError):
    """Raised when a git operation fails."""


class CliExecutionError(BmadError):
    """Raised when external CLI execution fails."""


class AgentError(BmadError):
    """Raised when an agent fails to complete its task."""


class StoryValidationError(BmadError):
    """Raised when story validation fails."""
