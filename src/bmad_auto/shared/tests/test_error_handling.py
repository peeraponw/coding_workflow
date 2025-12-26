"""Tests for error handling utilities (Story 2.5)."""

import pytest

from bmad_auto.shared.consts import (
    ERROR_API,
    ERROR_RATE_LIMIT,
    ERROR_UNEXPECTED,
    STATUS_PAUSED,
)
from bmad_auto.shared.error_handling import (
    create_paused_state_with_error,
    get_error_message_for_type,
)
from bmad_auto.shared.exceptions import WorkflowPausedError


class TestErrorTypeConstants:
    """Test error type constants exist and have correct values."""

    def test_error_rate_limit_constant(self) -> None:
        """Test ERROR_RATE_LIMIT constant exists."""
        assert ERROR_RATE_LIMIT == "rate_limit"

    def test_error_api_constant(self) -> None:
        """Test ERROR_API constant exists."""
        assert ERROR_API == "api_error"

    def test_error_unexpected_constant(self) -> None:
        """Test ERROR_UNEXPECTED constant exists."""
        assert ERROR_UNEXPECTED == "unexpected"


class TestCreatePausedStateWithError:
    """Test create_paused_state_with_error function."""

    def test_creates_paused_state_with_rate_limit_error(self) -> None:
        """Test creating paused state with rate limit error."""
        from datetime import datetime, timezone

        from bmad_auto.core.state import (
            CompletedStory,
            CurrentStorySection,
            ErrorSection,
            StoriesSection,
            WorkflowSection,
            WorkflowState,
        )

        original_state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )

        paused_state = create_paused_state_with_error(
            original_state,
            error_type=ERROR_RATE_LIMIT,
            error_message="Rate limit exceeded",
        )

        assert paused_state.workflow.status == STATUS_PAUSED
        assert paused_state.error.type == ERROR_RATE_LIMIT
        assert paused_state.error.message == "Rate limit exceeded"
        assert paused_state.error.phase == original_state.current_story.phase

    def test_creates_paused_state_with_api_error(self) -> None:
        """Test creating paused state with API error."""
        from bmad_auto.core.state import WorkflowState

        original_state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )

        paused_state = create_paused_state_with_error(
            original_state,
            error_type=ERROR_API,
            error_message="API timeout",
        )

        assert paused_state.workflow.status == STATUS_PAUSED
        assert paused_state.error.type == ERROR_API
        assert paused_state.error.message == "API timeout"

    def test_creates_paused_state_with_unexpected_error(self) -> None:
        """Test creating paused state with unexpected error."""
        from bmad_auto.core.state import WorkflowState

        original_state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )

        paused_state = create_paused_state_with_error(
            original_state,
            error_type=ERROR_UNEXPECTED,
            error_message="Unexpected error occurred",
        )

        assert paused_state.workflow.status == STATUS_PAUSED
        assert paused_state.error.type == ERROR_UNEXPECTED
        assert paused_state.error.message == "Unexpected error occurred"

    def test_preserves_completed_stories(self) -> None:
        """Test that completed stories are preserved."""
        from datetime import datetime, timezone

        from bmad_auto.core.state import (
            CompletedStory,
            CurrentStorySection,
            ErrorSection,
            StoriesSection,
            WorkflowSection,
            WorkflowState,
        )

        original_state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status="in-progress",
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=2,
                completed=[
                    CompletedStory(story_id="1-1", commit="abc123"),
                    CompletedStory(story_id="1-2", commit="def456"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-3",
                phase="dev",
                iteration=1,
                started_at=datetime.now(timezone.utc),
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        paused_state = create_paused_state_with_error(
            original_state,
            error_type=ERROR_API,
            error_message="API error",
        )

        assert len(paused_state.stories.completed) == 2
        assert paused_state.stories.completed[0].story_id == "1-1"
        assert paused_state.stories.completed[0].commit == "abc123"


class TestGetErrorMessageForType:
    """Test get_error_message_for_type function."""

    def test_rate_limit_message(self) -> None:
        """Test error message for rate limit."""
        message = get_error_message_for_type(ERROR_RATE_LIMIT)
        assert "rate limit" in message.lower()
        assert "resume" in message.lower()

    def test_api_error_message(self) -> None:
        """Test error message for API error."""
        message = get_error_message_for_type(ERROR_API)
        assert "api" in message.lower() or "error" in message.lower()
        assert "resume" in message.lower()

    def test_unexpected_error_message(self) -> None:
        """Test error message for unexpected error."""
        message = get_error_message_for_type(ERROR_UNEXPECTED)
        assert "unexpected" in message.lower() or "error" in message.lower()


class TestWorkflowPausedError:
    """Test WorkflowPausedError exception."""

    def test_workflow_paused_error_exists(self) -> None:
        """Test WorkflowPausedError can be raised and caught."""
        with pytest.raises(WorkflowPausedError):
            raise WorkflowPausedError("Workflow paused")

    def test_workflow_paused_error_is_bmad_auto_error(self) -> None:
        """Test WorkflowPausedError inherits from BmadAutoError."""
        from bmad_auto.shared.exceptions import BmadAutoError

        assert issubclass(WorkflowPausedError, BmadAutoError)

        # Can be caught as base exception
        try:
            raise WorkflowPausedError("test")
        except BmadAutoError:
            pass  # Expected
