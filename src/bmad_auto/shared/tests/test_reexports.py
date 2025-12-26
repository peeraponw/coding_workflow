"""Tests for bmad_auto.shared package re-exports."""


def test_exit_codes_are_exported() -> None:
    """Test that exit code constants are exported from shared package."""
    from bmad_auto.shared import (
        EXIT_CONFIG_ERROR,
        EXIT_ERROR,
        EXIT_PAUSED,
        EXIT_SUCCESS,
    )

    assert EXIT_SUCCESS == 0
    assert EXIT_ERROR == 1
    assert EXIT_PAUSED == 2
    assert EXIT_CONFIG_ERROR == 3


def test_agent_constants_are_exported() -> None:
    """Test that agent constants are exported from shared package."""
    from bmad_auto.shared import AGENT_DEV, AGENT_REVIEWER, AGENT_SM

    assert AGENT_SM == "sm"
    assert AGENT_DEV == "dev"
    assert AGENT_REVIEWER == "reviewer"


def test_phase_constants_are_exported() -> None:
    """Test that phase constants are exported from shared package."""
    from bmad_auto.shared import PHASE_DEV, PHASE_REVIEW, PHASE_SM

    assert PHASE_SM == "sm"
    assert PHASE_DEV == "dev"
    assert PHASE_REVIEW == "review"


def test_status_constants_are_exported() -> None:
    """Test that status constants are exported from shared package."""
    from bmad_auto.shared import (
        STATUS_COMPLETED,
        STATUS_FAILED,
        STATUS_IN_PROGRESS,
        STATUS_PAUSED,
        STATUS_PENDING,
    )

    assert STATUS_PENDING == "pending"
    assert STATUS_IN_PROGRESS == "in-progress"
    assert STATUS_PAUSED == "paused"
    assert STATUS_COMPLETED == "completed"
    assert STATUS_FAILED == "failed"


def test_types_are_exported() -> None:
    """Test that type aliases are exported from shared package."""
    from bmad_auto.shared import (
        AgentId,
        EpicKey,
        EpicPath,
        Phase,
        StoryId,
        StoryKey,
        StoryStatus,
        WorkflowState,
    )

    # Type aliases should be in the module
    assert StoryId is not None
    assert StoryKey is not None
    assert EpicKey is not None
    assert EpicPath is not None
    assert AgentId is not None
    assert Phase is not None
    assert StoryStatus is not None
    assert WorkflowState is not None


def test_exceptions_are_exported() -> None:
    """Test that exceptions are exported from shared package."""
    from bmad_auto.shared import (
        AgentError,
        BmadAutoError,
        ConfigError,
        StateCorruptionError,
        WorkflowPausedError,
    )

    # Verify exception hierarchy
    assert issubclass(BmadAutoError, Exception)
    assert issubclass(ConfigError, BmadAutoError)
    assert issubclass(StateCorruptionError, BmadAutoError)
    assert issubclass(AgentError, BmadAutoError)
    assert issubclass(WorkflowPausedError, BmadAutoError)


def test_logging_utilities_are_exported() -> None:
    """Test that logging utilities are exported from shared package."""
    from bmad_auto.shared import (
        DEV_COLOR,
        REVIEWER_COLOR,
        SM_COLOR,
        console,
        get_logger,
        print_dev,
        print_reviewer,
        print_sm,
    )

    # Color constants
    assert SM_COLOR == "blue"
    assert DEV_COLOR == "green"
    assert REVIEWER_COLOR == "yellow"

    # Logger function
    assert callable(get_logger)

    # Console
    assert console is not None

    # Print functions
    assert callable(print_sm)
    assert callable(print_dev)
    assert callable(print_reviewer)


def test_shared_package_has_expected_all_exports() -> None:
    """Test that __all__ is properly defined in shared package."""
    from bmad_auto import shared

    expected_exports = {
        # Logging
        "get_logger",
        "console",
        "SM_COLOR",
        "DEV_COLOR",
        "REVIEWER_COLOR",
        "print_sm",
        "print_dev",
        "print_reviewer",
        # Exit codes
        "EXIT_SUCCESS",
        "EXIT_ERROR",
        "EXIT_PAUSED",
        "EXIT_CONFIG_ERROR",
        # Agents
        "AGENT_SM",
        "AGENT_DEV",
        "AGENT_REVIEWER",
        # Phases
        "PHASE_SM",
        "PHASE_DEV",
        "PHASE_REVIEW",
        # Status
        "STATUS_PENDING",
        "STATUS_IN_PROGRESS",
        "STATUS_PAUSED",
        "STATUS_COMPLETED",
        "STATUS_FAILED",
        # Types
        "StoryId",
        "StoryKey",
        "EpicKey",
        "EpicPath",
        "AgentId",
        "Phase",
        "StoryStatus",
        "WorkflowState",
        # Exceptions
        "BmadAutoError",
        "ConfigError",
        "StateCorruptionError",
        "AgentError",
        "WorkflowPausedError",
    }

    assert set(shared.__all__) == expected_exports
