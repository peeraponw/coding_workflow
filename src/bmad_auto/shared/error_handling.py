"""Error handling utilities for graceful workflow pause.

Provides functions to create paused states with error information,
which will be used by the orchestrator (Epic 3) for error recovery.
"""

from pathlib import Path

from bmad_auto.core.state import WorkflowState, WorkflowSection, save
from bmad_auto.shared.consts import (
    ERROR_API,
    ERROR_RATE_LIMIT,
    ERROR_UNEXPECTED,
    STATUS_PAUSED,
)


def create_paused_state_with_error(
    state: WorkflowState,
    error_type: str,
    error_message: str,
) -> WorkflowState:
    """Create a paused state with error information from current state.

    This function creates a new WorkflowState with the status set to paused
    and error information populated. It preserves all other state including
    completed stories, current story position, etc.

    Args:
        state: The current workflow state.
        error_type: Type of error (ERROR_RATE_LIMIT, ERROR_API, ERROR_UNEXPECTED).
        error_message: Human-readable error message.

    Returns:
        A new WorkflowState with paused status and error information.

    Example:
        >>> paused_state = create_paused_state_with_error(
        ...     current_state,
        ...     error_type=ERROR_RATE_LIMIT,
        ...     error_message="Rate limit exceeded",
        ... )
        >>> save(paused_state, state_path)
    """
    # Create new workflow section with paused status
    paused_workflow = WorkflowSection(
        epic_path=state.workflow.epic_path,
        status=STATUS_PAUSED,
        branch=state.workflow.branch,
    )

    # Create new state with error information
    from bmad_auto.core.state import ErrorSection

    paused_state = WorkflowState(
        workflow=paused_workflow,
        stories=state.stories,  # Preserves completed stories
        current_story=state.current_story,  # Preserves current position
        error=ErrorSection(
            type=error_type,
            message=error_message,
            phase=state.current_story.phase,  # Record where error occurred
        ),
    )

    return paused_state


def save_paused_state(
    state: WorkflowState,
    state_path: Path,
    error_type: str,
    error_message: str,
) -> WorkflowState:
    """Save a paused state with error information to disk.

    This is a convenience function that combines create_paused_state_with_error
    and save, used by the orchestrator when handling errors.

    Args:
        state: The current workflow state.
        state_path: Path where state file should be saved.
        error_type: Type of error.
        error_message: Human-readable error message.

    Returns:
        The paused state that was saved.

    Example:
        >>> try:
        ...     await execute_story(state)
        ... except RateLimitError as e:
        ...     save_paused_state(state, state_path, ERROR_RATE_LIMIT, str(e))
    """
    paused_state = create_paused_state_with_error(
        state,
        error_type=error_type,
        error_message=error_message,
    )
    save(paused_state, state_path)
    return paused_state


def get_error_message_for_type(error_type: str) -> str:
    """Get a user-friendly error message for an error type.

    Args:
        error_type: The error type constant.

    Returns:
        A user-friendly error message with resume instructions.

    Raises:
        ValueError: If error_type is unknown.
    """
    messages = {
        ERROR_RATE_LIMIT: (
            "Rate limit exceeded. The API has limited the number of requests.\n"
            "Run 'bmad-auto resume' to continue after the rate limit resets."
        ),
        ERROR_API: (
            "API error occurred. There was a problem communicating with the API.\n"
            "Run 'bmad-auto resume' to retry after checking the issue."
        ),
        ERROR_UNEXPECTED: (
            "An unexpected error occurred. Please check the logs for details.\n"
            "Run 'bmad-auto resume' to continue after addressing the issue."
        ),
    }

    if error_type not in messages:
        raise ValueError(f"Unknown error type: {error_type}")

    return messages[error_type]


def get_exit_code_for_error_type(error_type: str) -> int:
    """Get the appropriate exit code for an error type.

    For rate limit and API errors, returns EXIT_PAUSED (2).
    For unexpected errors, returns EXIT_ERROR (1).

    Args:
        error_type: The error type constant.

    Returns:
        The appropriate exit code constant value.

    Raises:
        ValueError: If error_type is unknown.
    """
    from bmad_auto.shared.consts import EXIT_ERROR, EXIT_PAUSED

    paused_errors = {ERROR_RATE_LIMIT, ERROR_API}

    if error_type in paused_errors:
        return EXIT_PAUSED
    elif error_type == ERROR_UNEXPECTED:
        return EXIT_ERROR
    else:
        raise ValueError(f"Unknown error type: {error_type}")
