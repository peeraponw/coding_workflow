"""Workflow state model for bmad-auto.

Defines the complete state structure for tracking epic execution progress.
Matches the YAML state format from architecture documentation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CompletedStory:
    """A completed story with its commit hash."""

    story_id: str
    commit: str


@dataclass(frozen=True)
class WorkflowSection:
    """Workflow-level state (epic path, status, branch)."""

    epic_path: str
    status: str  # STATUS_* constants from shared/consts.py
    branch: str


@dataclass(frozen=True)
class StoriesSection:
    """Stories tracking (total count, current index, completed list)."""

    total: int
    current_index: int
    completed: list[CompletedStory]


@dataclass(frozen=True)
class CurrentStorySection:
    """Current story being processed."""

    id: str
    phase: str  # PHASE_* constants from shared/consts.py
    iteration: int
    started_at: datetime


@dataclass(frozen=True)
class ErrorSection:
    """Error information (all fields None when no error)."""

    type: str | None
    message: str | None
    phase: str | None


@dataclass(frozen=True)
class WorkflowState:
    """Complete workflow state for epic execution.

    This state is persisted to YAML and loaded to resume execution.
    All sections are frozen (immutable) - create new instances for state transitions.
    """

    workflow: WorkflowSection
    stories: StoriesSection
    current_story: CurrentStorySection
    error: ErrorSection

    @staticmethod
    def new(epic_path: str, story_count: int, branch: str) -> "WorkflowState":
        """Create initial workflow state for a new epic execution.

        Args:
            epic_path: Path to the epic markdown file.
            story_count: Total number of stories in the epic.
            branch: Git branch name for this epic.

        Returns:
            New WorkflowState in pending status with first story in SM phase.
        """
        from bmad_auto.shared.consts import PHASE_SM, STATUS_PENDING

        return WorkflowState(
            workflow=WorkflowSection(
                epic_path=epic_path,
                status=STATUS_PENDING,
                branch=branch,
            ),
            stories=StoriesSection(
                total=story_count,
                current_index=0,
                completed=[],
            ),
            current_story=CurrentStorySection(
                id="story-1",
                phase=PHASE_SM,
                iteration=1,
                started_at=datetime.now(timezone.utc),
            ),
            error=ErrorSection(type=None, message=None, phase=None),
        )

    def to_dict(self) -> dict:
        """Convert state to YAML-compatible dict.

        Returns:
            Nested dict structure matching YAML state format.
        """
        return {
            "workflow": {
                "epic_path": self.workflow.epic_path,
                "status": self.workflow.status,
                "branch": self.workflow.branch,
            },
            "stories": {
                "total": self.stories.total,
                "current_index": self.stories.current_index,
                "completed": [
                    {"story_id": s.story_id, "commit": s.commit}
                    for s in self.stories.completed
                ],
            },
            "current_story": {
                "id": self.current_story.id,
                "phase": self.current_story.phase,
                "iteration": self.current_story.iteration,
                "started_at": self.current_story.started_at.isoformat(),
            },
            "error": {
                "type": self.error.type,
                "message": self.error.message,
                "phase": self.error.phase,
            },
        }

    @staticmethod
    def from_dict(data: dict) -> "WorkflowState":
        """Create WorkflowState from YAML-compatible dict.

        Args:
            data: Nested dict from YAML state file.

        Returns:
            WorkflowState instance.
        """
        workflow_data = data["workflow"]
        stories_data = data["stories"]
        current_story_data = data["current_story"]
        error_data = data["error"]

        return WorkflowState(
            workflow=WorkflowSection(
                epic_path=workflow_data["epic_path"],
                status=workflow_data["status"],
                branch=workflow_data["branch"],
            ),
            stories=StoriesSection(
                total=stories_data["total"],
                current_index=stories_data["current_index"],
                completed=[
                    CompletedStory(story_id=s["story_id"], commit=s["commit"])
                    for s in stories_data["completed"]
                ],
            ),
            current_story=CurrentStorySection(
                id=current_story_data["id"],
                phase=current_story_data["phase"],
                iteration=current_story_data["iteration"],
                started_at=datetime.fromisoformat(current_story_data["started_at"]),
            ),
            error=ErrorSection(
                type=error_data["type"],
                message=error_data["message"],
                phase=error_data["phase"],
            ),
        )
