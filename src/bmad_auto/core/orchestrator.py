"""Story loop orchestrator for bmad-auto.

Orchestrates the SM → Dev → Review loop for epic execution.
Owns workflow state transitions and delegates to agents for execution.
"""

import re
from dataclasses import dataclass, replace
from pathlib import Path

import typer

from bmad_auto.agents.base import AgentProtocol
from bmad_auto.agents.prompts import (
    build_dev_command,
    build_reviewer_command,
    build_sm_command,
)
from bmad_auto.core.config import UserConfig
from bmad_auto.core.state import WorkflowState, save
from bmad_auto.features.git_integration import GitHandler
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
    git_config: UserConfig  # For git.auto_branch, git.branch_prefix


def derive_branch_name(epic_path: str, prefix: str) -> str:
    """Derive git branch name from epic file path.

    Args:
        epic_path: Path to epic file (e.g., "docs/epics/epic-001.md")
        prefix: Branch prefix from config (e.g., "epic/", "feature/")

    Returns:
        Sanitized branch name (e.g., "epic/epic-001")
    """
    # Get filename without extension
    filename = Path(epic_path).stem  # "epic-001"

    # Sanitize for git branch naming
    # Replace spaces and invalid chars with hyphens
    safe_name = re.sub(r"[~^:?*\[\]\\ .]+", "-", filename)
    # Remove double dots (invalid in git branch names)
    safe_name = safe_name.replace("..", "")
    # Remove leading/trailing hyphens
    safe_name = safe_name.strip("-")
    # Replace multiple hyphens with single
    safe_name = re.sub(r"-+", "-", safe_name)

    # Apply prefix
    if prefix and not prefix.endswith("/"):
        prefix = f"{prefix}/"

    return f"{prefix}{safe_name}"


def build_commit_message(epic_path: str, story_id: str, summary: str) -> str:
    """Build semantic commit message for story completion.

    Args:
        epic_path: Path to epic file (e.g., "epics/epic-001.md")
        story_id: Story identifier (e.g., "story-1")
        summary: Implementation summary

    Returns:
        Formatted commit message
    """
    # Extract epic name from path
    epic_name = Path(epic_path).stem  # "epic-001"

    # Build title: feat(epic-XXX): Story N - Title
    title = f"feat({epic_name}): {story_id}"

    # Build body with summary and metadata
    body = f"""{summary}

Story: {epic_path}/{story_id}
Reviewed-by: bmad-auto"""

    return f"{title}\n\n{body}"


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
        self.git = GitHandler(Path(config.working_dir))

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
        # Create feature branch if configured
        if self.config.git_config.git.auto_branch:
            branch_name = derive_branch_name(
                state.workflow.epic_path, self.config.git_config.git.branch_prefix
            )

            if self.git.branch_exists(branch_name):
                # Branch exists - ask user to confirm using existing branch
                typer.echo(f"[yellow]Warning:[/yellow] Branch '{branch_name}' already exists.")
                if not typer.confirm(f"Use existing branch '{branch_name}'?", default=False):
                    state = self._set_workflow_status(state, STATUS_FAILED)
                    return self._save_state(state)
                self.git.checkout_branch(branch_name)
            else:
                self.git.create_branch(branch_name)

            # Update state with branch name
            state = replace(
                state,
                workflow=replace(state.workflow, branch=branch_name),
            )

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
                state, commit_hash = await self._run_story(state, story_id)
                state = self._mark_story_completed(state, story_id, commit_hash)
                state = self._save_state(state)
            except Exception as e:
                return self._handle_error(state, str(e), PHASE_DEV)

        # All stories complete
        state = self._set_workflow_status(state, STATUS_COMPLETED)
        return self._save_state(state)

    async def _run_story(
        self, state: WorkflowState, story_id: str
    ) -> tuple[WorkflowState, str | None]:
        """Run a single story through SM → Dev → Review loop.

        Args:
            state: Current workflow state
            story_id: ID of the story to run

        Returns:
            Tuple of (updated_workflow_state, commit_hash or None)
        """
        # SM phase
        state = await self._run_sm_phase(state, story_id)

        commit_hash = None

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
                # Commit changes if auto-commit is enabled
                commit_hash, state = self._commit_story(
                    state, story_id, impl_summary="Implementation completed"
                )
                return state, commit_hash

        # Max iterations reached - pause workflow
        return self._pause_with_review_error(state), None

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

    def _commit_story(
        self, state: WorkflowState, story_id: str, impl_summary: str
    ) -> tuple[str | None, WorkflowState]:
        """Commit story changes after review approval.

        Args:
            state: Current workflow state
            story_id: ID of the story
            impl_summary: Implementation summary from dev agent

        Returns:
            Tuple of (commit_hash or None, updated_state)
        """
        from bmad_auto.shared.logging import get_logger
        from bmad_auto.features.git_integration import GitError

        logger = get_logger(__name__)

        if not self.config.git_config.git.auto_commit:
            logger.info("Auto-commit disabled, skipping commit")
            return None, state

        try:
            # Stage all changes
            self.git.stage_all()

            # Check if there are changes to commit
            if not self.git.has_staged_changes():
                logger.warning("No changes to commit for story", extra={"story_id": story_id})
                return None, state

            # Build commit message
            message = build_commit_message(
                epic_path=state.workflow.epic_path,
                story_id=story_id,
                summary=impl_summary,
            )

            # Commit and get hash
            commit_hash = self.git.commit(message)
            logger.info(
                "Committed story",
                extra={"story_id": story_id, "commit_hash": commit_hash},
            )
            return commit_hash, state
        except GitError as e:
            logger.error(
                "Failed to commit story",
                extra={"story_id": story_id, "error": str(e)},
            )
            # Don't fail the workflow, just log the error and continue
            return None, state

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
        self, state: WorkflowState, story_id: str, commit_hash: str | None = None
    ) -> WorkflowState:
        """Mark a story as completed.

        Args:
            state: Current workflow state
            story_id: ID of the completed story
            commit_hash: Git commit hash (optional if auto-commit disabled)

        Returns:
            Updated workflow state
        """
        from bmad_auto.core.state import CompletedStory

        # Use commit hash if available, otherwise use placeholder
        commit = commit_hash or "no-commit"

        completed_story = CompletedStory(story_id=story_id, commit=commit)

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
