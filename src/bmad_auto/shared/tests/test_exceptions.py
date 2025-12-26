"""Tests for shared exceptions."""

import pytest

from bmad_auto.shared.exceptions import (
    AgentError,
    BmadAutoError,
    ConfigError,
    StateCorruptionError,
    WorkflowPausedError,
)


class TestBmadAutoError:
    """Test base exception."""

    def test_bmad_auto_error_is_exception(self) -> None:
        """BmadAutoError should be an Exception subclass."""
        assert issubclass(BmadAutoError, Exception)

    def test_bmad_auto_error_can_be_raised(self) -> None:
        """BmadAutoError should be raisable."""
        with pytest.raises(BmadAutoError):
            raise BmadAutoError("Test error")


class TestConfigError:
    """Test ConfigError exception."""

    def test_config_error_is_bmad_auto_error(self) -> None:
        """ConfigError should be a BmadAutoError subclass."""
        assert issubclass(ConfigError, BmadAutoError)

    def test_config_error_can_be_raised(self) -> None:
        """ConfigError should be raisable."""
        with pytest.raises(ConfigError):
            raise ConfigError("Invalid config")

    def test_config_error_can_be_caught_as_base(self) -> None:
        """ConfigError should be catchable as BmadAutoError."""
        with pytest.raises(BmadAutoError):
            raise ConfigError("Invalid config")


class TestStateCorruptionError:
    """Test StateCorruptionError exception."""

    def test_state_corruption_error_is_bmad_auto_error(self) -> None:
        """StateCorruptionError should be a BmadAutoError subclass."""
        assert issubclass(StateCorruptionError, BmadAutoError)

    def test_state_corruption_error_can_be_raised(self) -> None:
        """StateCorruptionError should be raisable."""
        with pytest.raises(StateCorruptionError):
            raise StateCorruptionError("Corrupted state")

    def test_state_corruption_error_can_be_caught_as_base(self) -> None:
        """StateCorruptionError should be catchable as BmadAutoError."""
        with pytest.raises(BmadAutoError):
            raise StateCorruptionError("Corrupted state")


class TestAgentError:
    """Test AgentError exception."""

    def test_agent_error_is_bmad_auto_error(self) -> None:
        """AgentError should be a BmadAutoError subclass."""
        assert issubclass(AgentError, BmadAutoError)

    def test_agent_error_can_be_raised(self) -> None:
        """AgentError should be raisable."""
        with pytest.raises(AgentError):
            raise AgentError("Agent failed")

    def test_agent_error_can_be_caught_as_base(self) -> None:
        """AgentError should be catchable as BmadAutoError."""
        with pytest.raises(BmadAutoError):
            raise AgentError("Agent failed")


class TestWorkflowPausedError:
    """Test WorkflowPausedError exception."""

    def test_workflow_paused_error_is_bmad_auto_error(self) -> None:
        """WorkflowPausedError should be a BmadAutoError subclass."""
        assert issubclass(WorkflowPausedError, BmadAutoError)

    def test_workflow_paused_error_can_be_raised(self) -> None:
        """WorkflowPausedError should be raisable."""
        with pytest.raises(WorkflowPausedError):
            raise WorkflowPausedError("Workflow paused")

    def test_workflow_paused_error_can_be_caught_as_base(self) -> None:
        """WorkflowPausedError should be catchable as BmadAutoError."""
        with pytest.raises(BmadAutoError):
            raise WorkflowPausedError("Workflow paused")
