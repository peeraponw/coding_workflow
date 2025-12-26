"""Tests for workflow orchestrator."""

from pathlib import Path

import pytest

from bmad_auto.agents.base import AgentResult
from bmad_auto.core.config import UserConfig, GitConfig, AgentsConfig, WorkflowConfig
from bmad_auto.core.orchestrator import (
    MAX_REVIEW_ITERATIONS,
    OrchestratorConfig,
    WorkflowOrchestrator,
)
from bmad_auto.core.state import WorkflowState
from bmad_auto.shared.consts import (
    STATUS_COMPLETED,
    STATUS_PAUSED,
)
from bmad_auto.core.orchestrator import derive_branch_name


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, result: AgentResult | None = None) -> None:
        self._result = result or AgentResult.ok("Success")
        self.calls: list[str] = []

    async def run(self, command: str) -> AgentResult:
        self.calls.append(command)
        return self._result


@pytest.fixture
def temp_state_file(tmp_path: Path) -> Path:
    """Create a temporary state file path."""
    return tmp_path / "state.yaml"


@pytest.fixture
def orchestrator_config(temp_state_file: Path, tmp_path: Path) -> OrchestratorConfig:
    """Create orchestrator configuration for testing."""
    # Create a minimal UserConfig for git settings
    git_config = UserConfig(
        workflow=WorkflowConfig(epic_path="docs/epics", state_file=".bmad-auto/state.yaml"),
        agents=AgentsConfig(
            sm_model="claude",
            dev_model="glm",
            reviewer_model="claude",
        ),
        git=GitConfig(
            auto_branch=False,  # Disable auto branch for most tests
            auto_commit=True,
            branch_prefix="epic/",
        ),
    )

    return OrchestratorConfig(
        sm_model="claude",
        dev_model="glm",
        reviewer_model="claude",
        working_dir=str(tmp_path),  # Use real temp path for git operations
        state_file=temp_state_file,
        git_config=git_config,
    )


class TestWorkflowOrchestratorInit:
    """Test orchestrator initialization."""

    def test_creates_orchestrator_with_config(self, orchestrator_config) -> None:
        """Should create orchestrator with configuration and agents."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent()

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        assert orchestrator.config == orchestrator_config
        assert orchestrator.sm_agent is sm_agent
        assert orchestrator.dev_agent is dev_agent
        assert orchestrator.reviewer_agent is reviewer_agent


class TestRunEpic:
    """Test epic execution."""

    @pytest.mark.asyncio
    async def test_runs_all_stories_in_sequence(
        self, orchestrator_config, temp_state_file
    ) -> None:
        """Should process each story in sequence."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Approved - looks good"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=2, branch="feat/epic-1"
        )
        story_ids = ["story-1", "story-2"]

        final_state = await orchestrator.run_epic(state, story_ids)

        assert final_state.workflow.status == STATUS_COMPLETED
        assert len(final_state.stories.completed) == 2

    @pytest.mark.asyncio
    async def test_saves_state_after_each_phase(
        self, orchestrator_config, temp_state_file
    ) -> None:
        """Should save state after each phase transition."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Approved"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )
        story_ids = ["story-1"]

        await orchestrator.run_epic(state, story_ids)

        # State file should exist
        assert temp_state_file.exists()


class TestStoryLoop:
    """Test SM → Dev → Review loop."""

    @pytest.mark.asyncio
    async def test_sm_phase_executes(self, orchestrator_config) -> None:
        """SM phase should execute and update state."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Approved"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        assert len(sm_agent.calls) == 1
        assert "/bmad:bmm:agents:sm" in sm_agent.calls[0]

    @pytest.mark.asyncio
    async def test_dev_and_review_phases_execute(
        self, orchestrator_config
    ) -> None:
        """Dev and Review phases should execute for each iteration."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Approved - looks good"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        assert len(dev_agent.calls) == 1
        assert len(reviewer_agent.calls) == 1
        assert "/bmad:bmm:workflows:dev-story" in dev_agent.calls[0]
        assert "/bmad:bmm:workflows:code-review" in reviewer_agent.calls[0]


class TestReviewIterationLoop:
    """Test review iteration handling."""

    @pytest.mark.asyncio
    async def test_approved_review_breaks_loop(self, orchestrator_config) -> None:
        """Approved review should exit the loop immediately."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Approved - looks good"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        # Should only run once (approved on first iteration)
        assert len(dev_agent.calls) == 1
        assert len(reviewer_agent.calls) == 1

    @pytest.mark.asyncio
    async def test_rejected_review_retries(self, orchestrator_config) -> None:
        """Rejected review should trigger another Dev → Review cycle."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Needs work - fix these issues"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        # Should run MAX_REVIEW_ITERATIONS times
        assert len(dev_agent.calls) == MAX_REVIEW_ITERATIONS
        assert len(reviewer_agent.calls) == MAX_REVIEW_ITERATIONS


class TestMaxIterationHandling:
    """Test max iteration pause behavior."""

    @pytest.mark.asyncio
    async def test_max_iterations_pauses_workflow(self, orchestrator_config) -> None:
        """Should pause workflow after max iterations reached."""
        sm_agent = MockAgent()
        dev_agent = MockAgent()
        reviewer_agent = MockAgent(AgentResult.ok("Needs work"))

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        assert result_state.workflow.status == STATUS_PAUSED
        assert result_state.error.type == "review_failed"
        error_msg = result_state.error.message or ""
        assert "Maximum review iterations" in error_msg


class TestReviewApprovalDetection:
    """Test review approval detection logic."""

    def test_detects_approval_keywords(self, orchestrator_config) -> None:
        """Should detect approval keywords in review output."""
        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=MockAgent(),
            dev_agent=MockAgent(),
            reviewer_agent=MockAgent(),
        )

        assert orchestrator._check_review_approved("Approved - looks good")
        assert orchestrator._check_review_approved("LGTM")
        assert orchestrator._check_review_approved("Passed review")

    def test_detects_rejection_keywords(self, orchestrator_config) -> None:
        """Should detect rejection keywords in review output."""
        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=MockAgent(),
            dev_agent=MockAgent(),
            reviewer_agent=MockAgent(),
        )

        assert not orchestrator._check_review_approved("Rejected - needs work")
        assert not orchestrator._check_review_approved("Failed review")
        assert not orchestrator._check_review_approved("Changes required")


class TestErrorHandling:
    """Test error handling in orchestrator."""

    @pytest.mark.asyncio
    async def test_sm_phase_failure_sets_error_state(
        self, orchestrator_config
    ) -> None:
        """SM phase failure should set error state."""
        sm_agent = MockAgent(AgentResult.fail("SM agent error"))
        dev_agent = MockAgent()
        reviewer_agent = MockAgent()

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )

        result_state, _ = await orchestrator._run_story(state, "story-1")

        assert result_state.workflow.status == "failed"
        error_msg = result_state.error.message or ""
        assert "SM agent error" in error_msg

    @pytest.mark.asyncio
    async def test_dev_phase_failure_sets_error_state(
        self, orchestrator_config
    ) -> None:
        """Dev phase failure should set error state."""
        sm_agent = MockAgent()
        dev_agent = MockAgent(AgentResult.fail("Dev agent error"))
        reviewer_agent = MockAgent()

        orchestrator = WorkflowOrchestrator(
            config=orchestrator_config,
            sm_agent=sm_agent,
            dev_agent=dev_agent,
            reviewer_agent=reviewer_agent,
        )

        state = WorkflowState.new(
            epic_path="epic.md", story_count=1, branch="feat/epic-1"
        )
        # Skip SM phase by starting directly at story
        state = await orchestrator._run_sm_phase(state, "story-1")

        result_state = await orchestrator._run_dev_phase(state, "story-1")

        assert result_state.workflow.status == "failed"
        error_msg = result_state.error.message or ""
        assert "Dev agent error" in error_msg


class TestBranchNaming:
    """Test branch name derivation from epic paths."""

    @pytest.mark.parametrize(
        "prefix,epic,expected",
        [
            ("feature/", "epic-001.md", "feature/epic-001"),
            ("epic/", "epic-001.md", "epic/epic-001"),
            ("", "epic-001.md", "epic-001"),
            ("feat/", "docs/epics/my-epic-file.md", "feat/my-epic-file"),
            ("", "epic with spaces.md", "epic-with-spaces"),
            ("user/", "Epic_With_Underscores.md", "user/Epic_With_Underscores"),
            ("", "epic-001", "epic-001"),  # No extension
            ("hotfix/", "emergency-fix-123.md", "hotfix/emergency-fix-123"),
        ],
    )
    def test_branch_naming_variations(self, prefix: str, epic: str, expected: str) -> None:
        """Should handle various epic paths and prefixes."""
        result = derive_branch_name(epic, prefix)
        assert result == expected

    def test_branch_naming_sanitization(self) -> None:
        """Should sanitize invalid characters for git branch names."""
        # Test special characters
        assert derive_branch_name("epic~test.md", "") == "epic-test"
        assert derive_branch_name("epic^test.md", "") == "epic-test"
        assert derive_branch_name("epic:test.md", "") == "epic-test"
        assert derive_branch_name("epic?test.md", "") == "epic-test"
        assert derive_branch_name("epic*test.md", "") == "epic-test"
        assert derive_branch_name("epic[test.md", "") == "epic-test"
        assert derive_branch_name("epic\\test.md", "") == "epic-test"

    def test_branch_naming_edge_cases(self) -> None:
        """Should handle edge cases in naming."""
        # Multiple consecutive hyphens
        assert derive_branch_name("epic--test.md", "") == "epic-test"
        # Leading/trailing hyphens
        assert derive_branch_name("-epic-test-.md", "") == "epic-test"
        # Multiple special characters
        assert derive_branch_name("epic~^test.md", "") == "epic-test"
