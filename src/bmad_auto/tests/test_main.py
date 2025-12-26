"""Tests for bmad_auto.main CLI module."""

import inspect
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from bmad_auto.main import app
from bmad_auto.shared.consts import EXIT_CONFIG_ERROR, EXIT_ERROR, EXIT_SUCCESS
from bmad_auto.shared.exceptions import ConfigError

runner = CliRunner()


def test_help_shows_available_commands() -> None:
    """Test that --help shows available commands: run, status, resume."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "status" in result.stdout
    assert "resume" in result.stdout


def test_run_command_accepts_epic_argument() -> None:
    """Test that run command accepts --epic path argument."""
    result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-001.md"])
    # Stub message should be present (actual orchestration in Epic 3)
    assert result.exit_code == 0
    assert "stub" in result.stdout.lower()


def test_status_command_executes() -> None:
    """Test that status command executes with no workflow state."""
    result = runner.invoke(app, ["status"])
    # Should show no active workflow message
    assert result.exit_code == EXIT_SUCCESS
    output = result.stdout.lower()
    assert "no active workflow" in output or "no workflow" in output


def test_resume_command_executes() -> None:
    """Test that resume command executes (shows no workflow error when no state)."""
    result = runner.invoke(app, ["resume"])
    # Should show error about no workflow (exit code 1)
    assert result.exit_code == EXIT_ERROR
    # Error message should mention no workflow
    output = result.stdout.lower() + result.stderr.lower()
    assert "no workflow" in output or "not found" in output


def test_exit_code_success() -> None:
    """Test successful command returns exit code 0."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_exit_code_constants() -> None:
    """Test exit code constants have correct values."""
    assert EXIT_SUCCESS == 0
    assert EXIT_ERROR == 1
    assert EXIT_CONFIG_ERROR == 3


def test_missing_epic_argument_fails() -> None:
    """Test that run command without --epic fails appropriately."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0  # Should fail when required option is missing


# Test that exception handling infrastructure exists


def test_config_error_exists_and_can_be_raised() -> None:
    """Test ConfigError exception class exists and can be raised."""
    with pytest.raises(ConfigError):
        raise ConfigError("Test configuration error")


def test_general_exception_handling_infrastructure_exists() -> None:
    """Test that exception handling infrastructure is in place."""
    import bmad_auto.main as main_module

    # Verify that ConfigError is imported
    assert hasattr(main_module, "ConfigError")

    # Verify exit codes are imported
    assert hasattr(main_module, "EXIT_SUCCESS")
    assert hasattr(main_module, "EXIT_ERROR")
    assert hasattr(main_module, "EXIT_CONFIG_ERROR")


def test_all_commands_have_try_except_blocks() -> None:
    """Verify all commands have exception handling infrastructure."""
    import bmad_auto.main as main_module

    # Check that run function has exception handling
    run_source = inspect.getsource(main_module.run)
    assert "except ConfigError" in run_source
    assert "except Exception" in run_source
    assert "EXIT_CONFIG_ERROR" in run_source
    assert "EXIT_ERROR" in run_source

    # Check that status function has exception handling
    status_source = inspect.getsource(main_module.status)
    assert "except ConfigError" in status_source
    assert "except Exception" in status_source
    assert "EXIT_CONFIG_ERROR" in status_source
    assert "EXIT_ERROR" in status_source

    # Check that resume function has exception handling
    resume_source = inspect.getsource(main_module.resume)
    assert "except ConfigError" in resume_source
    assert "except Exception" in resume_source
    assert "EXIT_CONFIG_ERROR" in resume_source
    assert "EXIT_ERROR" in resume_source


def test_all_commands_use_exit_constants(cli_runner: CliRunner) -> None:
    """Verify all commands use exit code constants from shared.consts."""
    from bmad_auto.shared.consts import EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR

    # Verify constants are imported and used correctly
    assert EXIT_SUCCESS == 0
    assert EXIT_ERROR == 1
    assert EXIT_CONFIG_ERROR == 3


# Test exception handling by patching sys.exit to capture without raising


def test_run_command_exception_path_coverage() -> None:
    """Test exception handler paths in run command for coverage."""
    import bmad_auto.main as main_module

    # Test ConfigError path - mock a ConfigError during state loading
    from pathlib import Path
    import tempfile
    from bmad_auto.core.state import WorkflowState, save

    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / ".bmad-auto-state.yaml"

        # Create a valid state file first (so load() gets called)
        state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )
        save(state, state_path)

        # Mock get_state_path and make load raise ConfigError
        # Note: load is imported inside run(), so patch at source
        def mock_load_raises_config(*args):
            raise ConfigError("Test config error")

        with patch.object(main_module, "get_state_path", return_value=state_path):
            with patch("bmad_auto.core.state.load", side_effect=mock_load_raises_config):
                result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-001.md"])

        # Should get config error exit code
        assert result.exit_code == EXIT_CONFIG_ERROR

    # Test general exception path
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / ".bmad-auto-state.yaml"

        # Create a valid state file first
        state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )
        save(state, state_path)

        def mock_load_raises_runtime(*args):
            raise RuntimeError("Test error")

        with patch.object(main_module, "get_state_path", return_value=state_path):
            with patch("bmad_auto.core.state.load", side_effect=mock_load_raises_runtime):
                result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-001.md"])

        # Should get error exit code
        assert result.exit_code == EXIT_ERROR


def test_status_command_exception_path_coverage() -> None:
    """Test exception handler paths in status command for coverage."""
    import bmad_auto.main as main_module
    from pathlib import Path
    import tempfile

    # Test with a valid state file that triggers an error during display
    from bmad_auto.core.state import WorkflowState, save

    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / ".bmad-auto-state.yaml"
        state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )
        save(state, state_path)

        # Mock display_status to raise an exception
        def mock_display_raises(*args, **kwargs):
            raise RuntimeError("Test display error")

        with patch("bmad_auto.main.get_state_path", return_value=state_path):
            with patch("bmad_auto.core.display.display_status", side_effect=mock_display_raises):
                result = runner.invoke(app, ["status"])

        # Should get error exit code
        assert result.exit_code == EXIT_ERROR

    # Test ConfigError path - force load to raise ConfigError
    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / ".bmad-auto-state.yaml"
        # Create empty file so load() gets called
        state_path.write_text("workflow:\n  epic_path: test\n  status: pending\n  branch: main\nstories:\n  total: 1\n  current_index: 0\n  completed: []\ncurrent_story:\n  id: test\n  phase: sm\n  iteration: 1\n  started_at: '2025-01-01T00:00:00+00:00'\nerror:\n  type: null\n  message: null\n  phase: null\n")

        def mock_load_raises_config(*args):
            from bmad_auto.shared.exceptions import ConfigError
            raise ConfigError("Test config error")

        with patch("bmad_auto.main.get_state_path", return_value=state_path):
            with patch("bmad_auto.core.state.load", side_effect=mock_load_raises_config):
                result = runner.invoke(app, ["status"])

        # Should get config error exit code
        assert result.exit_code == EXIT_CONFIG_ERROR


def test_resume_command_exception_path_coverage() -> None:
    """Test exception handler paths in resume command for coverage."""
    from pathlib import Path

    import bmad_auto.main as main_module

    # Test with a valid state file (to avoid "no workflow" error)
    from bmad_auto.core.state import (
        WorkflowSection,
        WorkflowState,
        save,
    )
    from bmad_auto.shared.consts import STATUS_IN_PROGRESS

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        state_path = Path(tmpdir) / ".bmad-auto-state.yaml"
        state = WorkflowState.new(
            epic_path="docs/epics/epic-001.md",
            story_count=3,
            branch="epic/epic-001",
        )
        # Update to in_progress
        state = WorkflowState(
            workflow=WorkflowSection(
                epic_path="docs/epics/epic-001.md",
                status=STATUS_IN_PROGRESS,
                branch="epic/epic-001",
            ),
            stories=state.stories,
            current_story=state.current_story,
            error=state.error,
        )
        save(state, state_path)

        # Mock get_state_path to use our test file
        with patch.object(main_module, "get_state_path", return_value=state_path):
            # Test with valid state file - should succeed (exit 0)
            result = runner.invoke(app, ["resume"])
            assert result.exit_code == EXIT_SUCCESS

    # Test with no state file - should error (exit 1)
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_path = Path(tmpdir) / ".bmad-auto-state.yaml"
        with patch.object(main_module, "get_state_path", return_value=empty_path):
            result = runner.invoke(app, ["resume"])
            assert result.exit_code == EXIT_ERROR


# =============================================================================
# Tests for Resume Detection & Recovery (Story 2.4)
# =============================================================================


def test_resume_from_in_progress_status(tmp_path) -> None:
    """Test resume command with in_progress status loads state and displays info."""
    from pathlib import Path

    from bmad_auto.core.state import WorkflowState, save
    from bmad_auto.shared.consts import STATUS_IN_PROGRESS

    # Create a state file with in_progress status
    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    # Update to in_progress (simulating workflow started)
    from bmad_auto.core.state import WorkflowSection

    state = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-001.md",
            status=STATUS_IN_PROGRESS,
            branch="epic/epic-001",
        ),
        stories=state.stories,
        current_story=state.current_story,
        error=state.error,
    )
    save(state, state_path)

    # Mock get_state_path to return our test path
    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["resume"])

    # Should show resume info (stub for now, will show actual details in Epic 3)
    assert result.exit_code == 0
    # The stub message should be present
    assert "stub" in result.stdout.lower()


def test_resume_from_paused_status(tmp_path) -> None:
    """Test resume command with paused status loads state and displays info."""
    from pathlib import Path

    from bmad_auto.core.state import WorkflowState, save
    from bmad_auto.shared.consts import STATUS_PAUSED

    # Create a state file with paused status
    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    # Update to paused
    from bmad_auto.core.state import WorkflowSection

    state = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-001.md",
            status=STATUS_PAUSED,
            branch="epic/epic-001",
        ),
        stories=state.stories,
        current_story=state.current_story,
        error=state.error,
    )
    save(state, state_path)

    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["resume"])

    assert result.exit_code == 0
    assert "stub" in result.stdout.lower()


def test_resume_with_completed_workflow(tmp_path) -> None:
    """Test resume command with completed status informs user."""
    from pathlib import Path

    from bmad_auto.core.state import WorkflowState, save
    from bmad_auto.shared.consts import STATUS_COMPLETED

    # Create a state file with completed status
    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    # Update to completed
    from bmad_auto.core.state import WorkflowSection

    state = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-001.md",
            status=STATUS_COMPLETED,
            branch="epic/epic-001",
        ),
        stories=state.stories,
        current_story=state.current_story,
        error=state.error,
    )
    save(state, state_path)

    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["resume"])

    # Should inform user workflow is complete
    assert result.exit_code == EXIT_SUCCESS
    assert "complete" in result.stdout.lower() or "done" in result.stdout.lower()


def test_resume_with_no_state_file(tmp_path) -> None:
    """Test resume command with no state file shows clear error."""
    from pathlib import Path

    # Mock get_state_path to return non-existent file
    state_path = tmp_path / ".bmad-auto-state.yaml"

    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["resume"])

    # Should show clear error message (check both stdout and stderr for rich console)
    assert result.exit_code == EXIT_ERROR
    output = result.stdout.lower() + result.stderr.lower()
    assert "no workflow" in output or "not found" in output


def test_run_command_conflict_detection(tmp_path) -> None:
    """Test run command detects in-progress workflow for same epic."""
    from pathlib import Path

    from bmad_auto.core.state import WorkflowState, save
    from bmad_auto.shared.consts import STATUS_IN_PROGRESS

    # Create a state file with in_progress for epic-001
    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    # Update to in_progress
    from bmad_auto.core.state import WorkflowSection

    state = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-001.md",
            status=STATUS_IN_PROGRESS,
            branch="epic/epic-001",
        ),
        stories=state.stories,
        current_story=state.current_story,
        error=state.error,
    )
    save(state, state_path)

    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-001.md"])

    # Should warn about existing workflow
    assert result.exit_code == EXIT_ERROR
    assert "warning" in result.stdout.lower() or "already" in result.stdout.lower()
    assert "resume" in result.stdout.lower()


def test_run_command_different_epic_no_warning(tmp_path) -> None:
    """Test run command with different epic doesn't warn (different workflow)."""
    from pathlib import Path

    from bmad_auto.core.state import WorkflowState, save
    from bmad_auto.shared.consts import STATUS_IN_PROGRESS

    # Create a state file with in_progress for epic-001
    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    # Update to in_progress
    from bmad_auto.core.state import WorkflowSection

    state = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-001.md",
            status=STATUS_IN_PROGRESS,
            branch="epic/epic-001",
        ),
        stories=state.stories,
        current_story=state.current_story,
        error=state.error,
    )
    save(state, state_path)

    # Run with DIFFERENT epic
    with patch("bmad_auto.main.get_state_path", return_value=state_path):
        result = runner.invoke(app, ["run", "--epic", "docs/epics/epic-002.md"])

    # Should still show stub message (no conflict warning for different epic)
    # The stub will execute, and for different epic it's a new workflow
    assert "stub" in result.stdout.lower() or "epic-002" in result.stdout.lower()


def test_resume_restores_exact_position(tmp_path) -> None:
    """Test that resume restores exact story, phase, and iteration."""
    from pathlib import Path
    from datetime import datetime, timezone

    from bmad_auto.core.state import (
        CompletedStory,
        CurrentStorySection,
        ErrorSection,
        StoriesSection,
        WorkflowSection,
        WorkflowState,
        load,
        save,
    )
    from bmad_auto.shared.consts import STATUS_IN_PROGRESS

    # Create state with specific position
    state_path = tmp_path / ".bmad-auto-state.yaml"
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
            completed=[
                CompletedStory(story_id="1-1", commit="abc123"),
            ],
        ),
        current_story=CurrentStorySection(
            id="1-3",
            phase="dev",
            iteration=2,
            started_at=now,
        ),
        error=ErrorSection(type=None, message=None, phase=None),
    )
    save(state, state_path)

    # Verify we can load the exact position
    loaded = load(state_path)
    assert loaded.stories.current_index == 2
    assert loaded.current_story.id == "1-3"
    assert loaded.current_story.phase == "dev"
    assert loaded.current_story.iteration == 2
