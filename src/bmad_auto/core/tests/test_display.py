"""Tests for bmad_auto.core.display module."""

from datetime import datetime, timezone, timedelta


from bmad_auto.core.display import (
    calculate_duration,
    format_time,
    display_status,
    display_no_workflow,
    display_paused_status,
    display_completion_summary,
)
from bmad_auto.core.state import (
    CompletedStory,
    CurrentStorySection,
    ErrorSection,
    StoriesSection,
    WorkflowSection,
    WorkflowState,
)
from bmad_auto.shared.consts import (
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
    STATUS_COMPLETED,
)


class TestCalculateDuration:
    """Tests for calculate_duration function."""

    def test_duration_seconds_only(self) -> None:
        """Test duration with only seconds."""
        started = datetime.now(timezone.utc) - timedelta(seconds=45)
        result = calculate_duration(started)
        assert result == "0m 45s"

    def test_duration_minutes_seconds(self) -> None:
        """Test duration with minutes and seconds."""
        started = datetime.now(timezone.utc) - timedelta(minutes=12, seconds=34)
        result = calculate_duration(started)
        assert result == "12m 34s"

    def test_duration_hours_minutes_seconds(self) -> None:
        """Test duration with hours, minutes, and seconds."""
        started = datetime.now(timezone.utc) - timedelta(hours=1, minutes=5, seconds=12)
        result = calculate_duration(started)
        assert result == "1h 05m 12s"

    def test_duration_zero(self) -> None:
        """Test duration that is effectively zero."""
        started = datetime.now(timezone.utc)
        result = calculate_duration(started)
        # Should be 0m 00s or 0m 01s depending on timing
        assert result.startswith("0m 0")


class TestFormatTime:
    """Tests for format_time function."""

    def test_format_time_basic(self) -> None:
        """Test basic time formatting."""
        dt = datetime(2025, 12, 26, 14, 23, 7, tzinfo=timezone.utc)
        result = format_time(dt)
        assert result == "14:23:07"

    def test_format_time_midnight(self) -> None:
        """Test formatting midnight time."""
        dt = datetime(2025, 12, 26, 0, 0, 0, tzinfo=timezone.utc)
        result = format_time(dt)
        assert result == "00:00:00"

    def test_format_time_end_of_day(self) -> None:
        """Test formatting end of day time."""
        dt = datetime(2025, 12, 26, 23, 59, 59, tzinfo=timezone.utc)
        result = format_time(dt)
        assert result == "23:59:59"


class TestDisplayStatus:
    """Tests for display_status function."""

    def test_display_in_progress_with_completed_stories(self, capsys) -> None:
        """Test displaying status with in-progress workflow and completed stories."""
        # Create state with completed stories
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=2,  # On story 3 (0-indexed)
                completed=[
                    CompletedStory(story_id="1-1", commit="abc1234"),
                    CompletedStory(story_id="1-2", commit="def5678"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-3",
                phase="dev",
                iteration=1,
                started_at=now - timedelta(minutes=12),
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out

        # Verify key elements are present
        assert "docs/epics/epic-001.md" in output
        assert "in-progress" in output
        assert "Story 3 of 5" in output
        assert '"1-3"' in output
        assert "Phase: dev" in output
        assert "Started:" in output
        assert "Duration:" in output
        assert "Completed Stories:" in output
        assert "abc1234" in output  # Short hash
        assert "def5678" in output
        assert "✓" in output or "Story" in output

    def test_display_status_with_iteration(self, capsys) -> None:
        """Test displaying status with iteration > 1 shows iteration count."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=0,
                completed=[],
            ),
            current_story=CurrentStorySection(
                id="1-1",
                phase="review",
                iteration=2,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out
        assert "review (iteration 2)" in output

    def test_display_status_no_completed_stories(self, capsys) -> None:
        """Test displaying status with no completed stories yet."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=3,
                current_index=0,
                completed=[],  # No completed stories
            ),
            current_story=CurrentStorySection(
                id="1-1",
                phase="sm",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out
        # Should still show current story but not completed stories section
        assert '"1-1"' in output
        assert "Phase: sm" in output
        # "Completed Stories" should not appear when empty
        assert "Completed Stories:" not in output


class TestDisplayNoWorkflow:
    """Tests for display_no_workflow function."""

    def test_display_no_workflow_message(self, capsys) -> None:
        """Test displaying no workflow message."""
        display_no_workflow()

        captured = capsys.readouterr()
        output = captured.out

        assert "No active workflow" in output
        assert "bmad-auto run --epic" in output


class TestDisplayPausedStatus:
    """Tests for display_paused_status function."""

    def test_display_paused_with_error(self, capsys) -> None:
        """Test displaying paused status with error details."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_PAUSED,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=2,
                completed=[
                    CompletedStory(story_id="1-1", commit="abc1234"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-3",
                phase="dev",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(
                type="rate_limit",
                message="API rate limit exceeded",
                phase="dev",
            ),
        )

        display_paused_status(state)

        captured = capsys.readouterr()
        output = captured.out

        assert "PAUSED" in output
        assert "API rate limit exceeded" in output
        assert "rate_limit" in output
        assert "dev" in output
        assert "Resume instructions:" in output
        assert "bmad-auto resume" in output

    def test_display_paused_without_error(self, capsys) -> None:
        """Test displaying paused status without error details."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_PAUSED,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=0,
                completed=[],
            ),
            current_story=CurrentStorySection(
                id="1-1",
                phase="sm",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(
                type=None,
                message=None,
                phase=None,
            ),
        )

        display_paused_status(state)

        captured = capsys.readouterr()
        output = captured.out

        # Should still show PAUSED and resume instructions
        assert "PAUSED" in output
        assert "Resume instructions:" in output


class TestDisplayCompletionSummary:
    """Tests for display_completion_summary function."""

    def test_display_completion_summary(self, capsys) -> None:
        """Test displaying completion summary."""
        now = datetime.now(timezone.utc) - timedelta(hours=1)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_COMPLETED,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=4,  # Last story completed
                completed=[
                    CompletedStory(story_id="1-1", commit="abc1234"),
                    CompletedStory(story_id="1-2", commit="def5678"),
                    CompletedStory(story_id="1-3", commit="ghi9012"),
                    CompletedStory(story_id="1-4", commit="jkl3456"),
                    CompletedStory(story_id="1-5", commit="mno7890"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-5",
                phase="review",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_completion_summary(state)

        captured = capsys.readouterr()
        output = captured.out

        assert "COMPLETED" in output
        assert "Total Stories: 5" in output
        assert "Total Commits: 5" in output
        assert "Branch: epic/epic-001" in output
        assert "Duration:" in output

class TestCommitHashFormatting:
    """Tests for commit hash formatting (AC: 4)."""

    def test_short_hash_format_is_7_chars(self, capsys) -> None:
        """Test commit hashes are truncated to 7 characters."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=3,
                current_index=1,
                completed=[
                    CompletedStory(story_id="1-1", commit="abc12345678901234567890"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-2",
                phase="dev",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out

        # Should show only first 7 chars
        assert "abc1234" in output
        assert "abc12345" not in output  # More than 7 chars should not appear

    def test_missing_commit_shows_pending(self, capsys) -> None:
        """Test stories without commits show 'pending'."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=2,
                current_index=1,
                completed=[
                    CompletedStory(story_id="1-1", commit=""),  # Empty commit
                    CompletedStory(story_id="1-2", commit=None),  # None commit
                ],
            ),
            current_story=CurrentStorySection(
                id="2-1",
                phase="sm",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out

        # Should show "pending" for missing commits
        assert output.count("pending") >= 2


class TestCurrentStoryDisplay:
    """Tests for current story display (AC: 2)."""

    def test_current_story_shows_all_details(self, capsys) -> None:
        """Test current story shows title, phase, iteration, started time."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=2,
                completed=[],
            ),
            current_story=CurrentStorySection(
                id="add-login-endpoint",
                phase="dev",
                iteration=1,
                started_at=now - timedelta(minutes=5),
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out

        assert '"add-login-endpoint"' in output
        assert "Phase: dev" in output
        assert "Iteration: 1" not in output  # Iteration only shows when > 1
        assert "Started:" in output
        assert "Duration:" in output

    def test_current_story_with_iteration(self, capsys) -> None:
        """Test current story with iteration > 1 shows iteration."""
        now = datetime.now(timezone.utc)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=5,
                current_index=0,
                completed=[],
            ),
            current_story=CurrentStorySection(
                id="1-1",
                phase="review",
                iteration=2,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_status(state)

        captured = capsys.readouterr()
        output = captured.out

        # Should show iteration count
        assert "review (iteration 2)" in output


class TestCompletionSummaryDisplay:
    """Additional tests for completion summary (AC: 3)."""

    def test_completion_summary_all_fields(self, capsys) -> None:
        """Test completion summary shows all required fields."""
        now = datetime.now(timezone.utc) - timedelta(minutes=45)
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_COMPLETED,
                branch="epic/epic-001",
            ),
            stories=StoriesSection(
                total=3,
                current_index=2,
                completed=[
                    CompletedStory(story_id="1-1", commit="a1b2c3d"),
                    CompletedStory(story_id="1-2", commit="e4f5g6h"),
                    CompletedStory(story_id="1-3", commit="i7j8k9l"),
                ],
            ),
            current_story=CurrentStorySection(
                id="1-3",
                phase="review",
                iteration=1,
                started_at=now,
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

        display_completion_summary(state)

        captured = capsys.readouterr()
        output = captured.out

        assert "COMPLETED" in output
        assert "Total Stories: 3" in output
        assert "Total Commits: 3" in output
        assert "Branch: epic/epic-001" in output
        assert "Duration:" in output
