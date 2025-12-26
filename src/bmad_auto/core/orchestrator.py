"""Story loop orchestrator for bmad-auto.

Orchestrates the SM → Dev → Review loop for epic execution.
Owns workflow state transitions and delegates to agents for execution.
"""

from dataclasses import dataclass, replace
from pathlib import Path

from bmad_auto.agents.base import AgentProtocol
from bmad_auto.agents.prompts import (
    build_dev_command,
    build_reviewer_command,
    build_sm_command,
)
from bmad_auto.core.state import WorkflowState, save
from bmad_auto.shared.consts import (
    PHASE_DEV,
    PHASE_REVIEW,
    PHASE_SM,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
)

# Maximum review iterations before pausing for manual intervention
MAX_REVIEW_ITERATIONS: int = 3


@dataclass(frozen=True)
class OrchestratorConfig:
    """Configuration for the workflow orchestrator."""

    sm_model: str
    dev_model: str
    reviewer_model: str
    working_dir: str
    state_file: Path


class WorkflowOrchestrator:
    """Orchestrates the SM → Dev → Review loop for epic execution.

    The orchestrator:
    - Owns workflow state transitions
    - Delegates to agents/ for execution
    - Delegates to state.py for I/O
    - Saves state after every phase transition
    """

    def __init__(
        self,
        config: OrchestratorConfig,
        sm_agent: AgentProtocol,
        dev_agent: AgentProtocol,
        reviewer_agent: AgentProtocol,
    ) -> None:
        """Initialize the orchestrator.

        Args:
            config: Orchestrator configuration
            sm_agent: SM agent instance
            dev_agent: Dev agent instance
            reviewer_agent: Reviewer agent instance
        """
        self.config = config
        self.sm_agent = sm_agent
        self.dev_agent = dev_agent
        self.reviewer_agent = reviewer_agent

    async def run_epic(
        self, state: WorkflowState, story_ids: list[str]
    ) -> WorkflowState:
        """Run all stories in the epic.

        Args:
            state: Initial workflow state
            story_ids: List of story IDs in the epic

        Returns:
            Final workflow state after all stories complete or error
        """
        # Mark workflow as in progress
        state = self._set_workflow_status(state, STATUS_IN_PROGRESS)
        state = self._save_state(state)

        # Process each story
        for story_index, story_id in enumerate(story_ids):
            state = self._update_current_story(
                state, story_id=story_id, phase=PHASE_SM, iteration=1
            )
            state = self._save_state(state)

            try:
                state = await self._run_story(state, story_id)
                state = self._mark_story_completed(state, story_id)
                state = self._save_state(state)
            except Exception as e:
                return self._handle_error(state, str(e), PHASE_DEV)

        # All stories complete
        state = self._set_workflow_status(state, STATUS_COMPLETED)
        return self._save_state(state)

    async def _run_story(
        self, state: WorkflowState, story_id: str
    ) -> WorkflowState:
        """Run a single story through SM → Dev → Review loop.

        Args:
            state: Current workflow state
            story_id: ID of the story to run

        Returns:
            Updated workflow state
        """
        # SM phase
        state = await self._run_sm_phase(state, story_id)

        # Dev → Review loop
        for iteration in range(1, MAX_REVIEW_ITERATIONS + 1):
            state = self._update_current_story(
                state, story_id=story_id, phase=PHASE_DEV, iteration=iteration
            )
            state = self._save_state(state)

            # Dev phase
            state = await self._run_dev_phase(state, story_id)

            # Review phase
            state = self._update_current_story(
                state, story_id=story_id, phase=PHASE_REVIEW, iteration=iteration
            )
            state = self._save_state(state)

            # Run review and check if approved
            approved, state = await self._run_review_phase(state, story_id)
            if approved:
                return state

        # Max iterations reached - pause workflow
        return self._pause_with_review_error(state)

    async def _run_sm_phase(
        self, state: WorkflowState, story_id: str
    ) -> WorkflowState:
        """Run SM phase to create/refine story.

        Args:
            state: Current workflow state
            story_id: ID of the story

        Returns:
            Updated workflow state
        """
        command = build_sm_command(int(story_id.split("-")[-1]))
        result = await self.sm_agent.run(command)

        if not result.success:
            state = self._handle_error(state, result.error or "SM phase failed", PHASE_SM)

        return state

    async def _run_dev_phase(
        self, state: WorkflowState, story_id: str
    ) -> WorkflowState:
        """Run Dev phase to implement story.

        Args:
            state: Current workflow state
            story_id: ID of the story

        Returns:
            Updated workflow state
        """
        command = build_dev_command(f"{story_id}.md")
        result = await self.dev_agent.run(command)

        if not result.success:
            state = self._handle_error(state, result.error or "Dev phase failed", PHASE_DEV)

        return state

    async def _run_review_phase(
        self, state: WorkflowState, story_id: str
    ) -> tuple[bool, WorkflowState]:
        """Run Review phase to validate implementation.

        Args:
            state: Current workflow state
            story_id: ID of the story

        Returns:
            Tuple of (approved, updated_state)
        """
        command = build_reviewer_command(f"{story_id}.md")
        result = await self.reviewer_agent.run(command)

        if not result.success:
            # Review failed - this is an error, not a rejection
            state = self._handle_error(
                state, result.error or "Review phase failed", PHASE_REVIEW
            )
            return False, state

        # Check if review passed (simple heuristic - look for approval keywords)
        approved = self._check_review_approved(result.output)
        return approved, state

    def _check_review_approved(self, review_output: str) -> bool:
        """Check if review output indicates approval.

        Args:
            review_output: Output from the reviewer agent

        Returns:
            True if approved, False otherwise
        """
        # Simple heuristic - look for approval indicators
        approved_indicators = ["approved", "looks good", "pass", "accepted"]
        rejected_indicators = ["rejected", "needs work", "failed", "changes required"]

        output_lower = review_output.lower()

        # Check for explicit rejection first
        for indicator in rejected_indicators:
            if indicator in output_lower:
                return False

        # Check for approval
        for indicator in approved_indicators:
            if indicator in output_lower:
                return True

        # Default to approve if no clear rejection indicators
        return True

    def _pause_with_review_error(self, state: WorkflowState) -> WorkflowState:
        """Pause workflow due to max review iterations reached.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state with paused status and error
        """
        state = replace(
            state,
            workflow=replace(
                state.workflow, status=STATUS_PAUSED
            ),
            error=replace(
                state.error,
                type="review_failed",
                message=f"Maximum review iterations ({MAX_REVIEW_ITERATIONS}) reached",
                phase=state.current_story.phase,
            ),
        )
        return self._save_state(state)

    def _handle_error(
        self, state: WorkflowState, message: str, phase: str
    ) -> WorkflowState:
        """Handle execution error by setting error state.

        Args:
            state: Current workflow state
            message: Error message
            phase: Phase where error occurred

        Returns:
            Updated workflow state with error
        """
        return replace(
            state,
            workflow=replace(state.workflow, status=STATUS_FAILED),
            error=replace(
                state.error,
                type="execution_error",
                message=message,
                phase=phase,
            ),
        )

    def _update_current_story(
        self, state: WorkflowState, story_id: str, phase: str, iteration: int
    ) -> WorkflowState:
        """Update current story section.

        Args:
            state: Current workflow state
            story_id: Story ID
            phase: Current phase
            iteration: Review iteration number

        Returns:
            Updated workflow state
        """
        return replace(
            state,
            current_story=replace(
                state.current_story,
                id=story_id,
                phase=phase,
                iteration=iteration,
            ),
        )

    def _mark_story_completed(
        self, state: WorkflowState, story_id: str
    ) -> WorkflowState:
        """Mark a story as completed.

        Args:
            state: Current workflow state
            story_id: ID of the completed story

        Returns:
            Updated workflow state
        """
        # Add to completed list (placeholder commit for now)
        # TODO: Get actual commit from git module
        from bmad_auto.core.state import CompletedStory

        completed_story = CompletedStory(story_id=story_id, commit="pending-commit")

        return replace(
            state,
            stories=replace(
                state.stories,
                completed=[*state.stories.completed, completed_story],
                current_index=state.stories.current_index + 1,
            ),
        )

    def _set_workflow_status(self, state: WorkflowState, status: str) -> WorkflowState:
        """Set workflow status.

        Args:
            state: Current workflow state
            status: New status value

        Returns:
            Updated workflow state
        """
        return replace(state, workflow=replace(state.workflow, status=status))

    def _save_state(self, state: WorkflowState) -> WorkflowState:
        """Save state to file.

        Args:
            state: Current workflow state

        Returns:
            The same state (for chaining)
        """
        save(state, self.config.state_file)
        return state
