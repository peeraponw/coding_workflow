"""Tests for shared constants."""


from bmad_auto.shared.consts import (
    # Exit codes
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_PAUSED,
    EXIT_CONFIG_ERROR,
    # Agents
    AGENT_SM,
    AGENT_DEV,
    AGENT_REVIEWER,
    # Phases
    PHASE_SM,
    PHASE_DEV,
    PHASE_REVIEW,
    # Status
    STATUS_PENDING,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
    STATUS_COMPLETED,
    STATUS_FAILED,
)


class TestExitCodes:
    """Test exit code constants."""

    def test_exit_success_is_zero(self) -> None:
        """EXIT_SUCCESS should be 0."""
        assert EXIT_SUCCESS == 0

    def test_exit_error_is_one(self) -> None:
        """EXIT_ERROR should be 1."""
        assert EXIT_ERROR == 1

    def test_exit_paused_is_two(self) -> None:
        """EXIT_PAUSED should be 2."""
        assert EXIT_PAUSED == 2

    def test_exit_config_error_is_three(self) -> None:
        """EXIT_CONFIG_ERROR should be 3."""
        assert EXIT_CONFIG_ERROR == 3


class TestAgentConstants:
    """Test agent constants."""

    def test_agent_sm_constant(self) -> None:
        """AGENT_SM should be 'sm'."""
        assert AGENT_SM == "sm"

    def test_agent_dev_constant(self) -> None:
        """AGENT_DEV should be 'dev'."""
        assert AGENT_DEV == "dev"

    def test_agent_reviewer_constant(self) -> None:
        """AGENT_REVIEWER should be 'reviewer'."""
        assert AGENT_REVIEWER == "reviewer"


class TestPhaseConstants:
    """Test phase constants."""

    def test_phase_sm_constant(self) -> None:
        """PHASE_SM should be 'sm'."""
        assert PHASE_SM == "sm"

    def test_phase_dev_constant(self) -> None:
        """PHASE_DEV should be 'dev'."""
        assert PHASE_DEV == "dev"

    def test_phase_review_constant(self) -> None:
        """PHASE_REVIEW should be 'review'."""
        assert PHASE_REVIEW == "review"


class TestStatusConstants:
    """Test status constants."""

    def test_status_pending_constant(self) -> None:
        """STATUS_PENDING should be 'pending'."""
        assert STATUS_PENDING == "pending"

    def test_status_in_progress_constant(self) -> None:
        """STATUS_IN_PROGRESS should be 'in-progress'."""
        assert STATUS_IN_PROGRESS == "in-progress"

    def test_status_paused_constant(self) -> None:
        """STATUS_PAUSED should be 'paused'."""
        assert STATUS_PAUSED == "paused"

    def test_status_completed_constant(self) -> None:
        """STATUS_COMPLETED should be 'completed'."""
        assert STATUS_COMPLETED == "completed"

    def test_status_failed_constant(self) -> None:
        """STATUS_FAILED should be 'failed'."""
        assert STATUS_FAILED == "failed"
