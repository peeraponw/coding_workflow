"""Workflow state model for bmad-auto.

Defines the complete state structure for tracking epic execution progress.
Matches the YAML state format from architecture documentation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml


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


def save(state: WorkflowState, path: Path) -> None:
    """Save workflow state atomically to a YAML file.

    Uses atomic write pattern (write to temp file, then rename) to ensure
    no corruption occurs if the process is interrupted during write.

    Args:
        state: The WorkflowState to persist.
        path: Destination path for the state file.

    Raises:
        OSError: If file write or rename operation fails.
    """
    temp_path = path.with_suffix(".tmp")
    try:
        # Write to temporary file first
        temp_path.write_text(yaml.dump(state.to_dict(), default_flow_style=False))
        # Atomic rename on POSIX systems
        temp_path.rename(path)
    except Exception:
        # Clean up temp file on failure
        temp_path.unlink(missing_ok=True)
        raise


def load(path: Path) -> WorkflowState:
    """Load workflow state from a YAML file with validation.

    Args:
        path: Path to the state file to load.

    Returns:
        Reconstructed WorkflowState.

    Raises:
        StateCorruptionError: If file is corrupted, malformed, or missing
            required fields.
        FileNotFoundError: If state file doesn't exist.
    """
    from bmad_auto.shared.exceptions import StateCorruptionError

    try:
        content = path.read_text()
        data = yaml.safe_load(content)
    except (yaml.YAMLError, OSError) as e:
        raise StateCorruptionError(
            f"State file '{path}' is corrupted or invalid YAML: {e}"
        ) from e

    # Validate required top-level sections
    required_sections = ["workflow", "stories", "current_story", "error"]
    for section in required_sections:
        if section not in data:
            raise StateCorruptionError(
                f"State file '{path}' is missing required section: {section}"
            )

    # Validate workflow section fields
    workflow_data = data["workflow"]
    required_workflow_fields = ["epic_path", "status", "branch"]
    for field in required_workflow_fields:
        if field not in workflow_data:
            raise StateCorruptionError(
                f"State file '{path}' is missing required field: workflow.{field}"
            )

    # Validate stories section fields
    stories_data = data["stories"]
    required_stories_fields = ["total", "current_index", "completed"]
    for field in required_stories_fields:
        if field not in stories_data:
            raise StateCorruptionError(
                f"State file '{path}' is missing required field: stories.{field}"
            )

    # Validate current_story section fields
    current_story_data = data["current_story"]
    required_current_story_fields = ["id", "phase", "iteration", "started_at"]
    for field in required_current_story_fields:
        if field not in current_story_data:
            raise StateCorruptionError(
                f"State file '{path}' is missing required field: current_story.{field}"
            )

    # Use from_dict which will handle data conversion and raise for invalid types
    try:
        return WorkflowState.from_dict(data)
    except (KeyError, ValueError, TypeError) as e:
        raise StateCorruptionError(
            f"State file '{path}' contains invalid data: {e}"
        ) from e
