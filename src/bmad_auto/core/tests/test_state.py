"""Tests for workflow state model."""

import pytest
from datetime import datetime, timezone

from bmad_auto.core.state import (
    CompletedStory,
    CurrentStorySection,
    ErrorSection,
    StoriesSection,
    WorkflowSection,
    WorkflowState,
)
from bmad_auto.shared.consts import (
    PHASE_DEV,
    PHASE_REVIEW,
    PHASE_SM,
    STATUS_COMPLETED,
    STATUS_IN_PROGRESS,
    STATUS_PENDING,
)


def test_workflow_section_dataclass() -> None:
    """Test WorkflowSection dataclass creation."""
    section = WorkflowSection(
        epic_path="docs/epics/epic-001.md",
        status=STATUS_IN_PROGRESS,
        branch="epic/epic-001",
    )

    assert section.epic_path == "docs/epics/epic-001.md"
    assert section.status == STATUS_IN_PROGRESS
    assert section.branch == "epic/epic-001"


def test_stories_section_dataclass() -> None:
    """Test StoriesSection dataclass creation."""
    completed = [
        CompletedStory(story_id="story-1", commit="abc123"),
        CompletedStory(story_id="story-2", commit="def456"),
    ]

    section = StoriesSection(total=5, current_index=2, completed=completed)

    assert section.total == 5
    assert section.current_index == 2
    assert len(section.completed) == 2
    assert section.completed[0].story_id == "story-1"
    assert section.completed[0].commit == "abc123"


def test_current_story_section_dataclass() -> None:
    """Test CurrentStorySection dataclass creation."""
    now = datetime.now(timezone.utc)
    section = CurrentStorySection(
        id="story-3",
        phase=PHASE_DEV,
        iteration=1,
        started_at=now,
    )

    assert section.id == "story-3"
    assert section.phase == PHASE_DEV
    assert section.iteration == 1
    assert section.started_at == now


def test_error_section_dataclass() -> None:
    """Test ErrorSection dataclass creation (with and without errors)."""
    # With error
    error = ErrorSection(
        type="ValidationError",
        message="Invalid epic format",
        phase=PHASE_SM,
    )

    assert error.type == "ValidationError"
    assert error.message == "Invalid epic format"
    assert error.phase == PHASE_SM

    # Without error (all None)
    no_error = ErrorSection(type=None, message=None, phase=None)
    assert no_error.type is None
    assert no_error.message is None
    assert no_error.phase is None


def test_workflow_state_full_creation() -> None:
    """Test complete WorkflowState creation with all sections."""
    now = datetime.now(timezone.utc)

    workflow = WorkflowSection(
        epic_path="docs/epics/epic-001.md",
        status=STATUS_IN_PROGRESS,
        branch="epic/epic-001",
    )

    completed = [
        CompletedStory(story_id="story-1", commit="abc123"),
        CompletedStory(story_id="story-2", commit="def456"),
    ]
    stories = StoriesSection(total=5, current_index=2, completed=completed)

    current_story = CurrentStorySection(
        id="story-3",
        phase=PHASE_DEV,
        iteration=1,
        started_at=now,
    )

    error = ErrorSection(type=None, message=None, phase=None)

    state = WorkflowState(
        workflow=workflow,
        stories=stories,
        current_story=current_story,
        error=error,
    )

    assert state.workflow.epic_path == "docs/epics/epic-001.md"
    assert state.stories.total == 5
    assert state.stories.current_index == 2
    assert len(state.stories.completed) == 2
    assert state.current_story.id == "story-3"
    assert state.current_story.phase == PHASE_DEV
    assert state.error.type is None


def test_workflow_state_factory_new() -> None:
    """Test WorkflowState.new() factory method for initial state."""
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )

    assert state.workflow.epic_path == "docs/epics/epic-001.md"
    assert state.workflow.status == STATUS_PENDING
    assert state.workflow.branch == "epic/epic-001"
    assert state.stories.total == 3
    assert state.stories.current_index == 0
    assert state.stories.completed == []
    assert state.current_story.id == "story-1"
    assert state.current_story.phase == PHASE_SM
    assert state.current_story.iteration == 1
    assert state.current_story.started_at is not None
    assert state.error.type is None


def test_workflow_state_to_dict_serialization() -> None:
    """Test to_dict() produces YAML-compatible dict."""
    now = datetime(2025, 12, 26, 14, 23, 7, tzinfo=timezone.utc)

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
                CompletedStory(story_id="story-1", commit="abc123"),
            ],
        ),
        current_story=CurrentStorySection(
            id="story-3",
            phase=PHASE_DEV,
            iteration=1,
            started_at=now,
        ),
        error=ErrorSection(type=None, message=None, phase=None),
    )

    result = state.to_dict()

    assert result == {
        "workflow": {
            "epic_path": "docs/epics/epic-001.md",
            "status": "in-progress",
            "branch": "epic/epic-001",
        },
        "stories": {
            "total": 5,
            "current_index": 2,
            "completed": [{"story_id": "story-1", "commit": "abc123"}],
        },
        "current_story": {
            "id": "story-3",
            "phase": "dev",
            "iteration": 1,
            "started_at": "2025-12-26T14:23:07+00:00",
        },
        "error": {"type": None, "message": None, "phase": None},
    }


def test_workflow_state_from_dict_deserialization() -> None:
    """Test from_dict() creates WorkflowState from dict."""
    data = {
        "workflow": {
            "epic_path": "docs/epics/epic-001.md",
            "status": "in-progress",
            "branch": "epic/epic-001",
        },
        "stories": {
            "total": 5,
            "current_index": 2,
            "completed": [
                {"story_id": "story-1", "commit": "abc123"},
                {"story_id": "story-2", "commit": "def456"},
            ],
        },
        "current_story": {
            "id": "story-3",
            "phase": "dev",
            "iteration": 1,
            "started_at": "2025-12-26T14:23:07+00:00",
        },
        "error": {"type": None, "message": None, "phase": None},
    }

    state = WorkflowState.from_dict(data)

    assert state.workflow.epic_path == "docs/epics/epic-001.md"
    assert state.workflow.status == "in-progress"
    assert state.stories.total == 5
    assert state.stories.current_index == 2
    assert len(state.stories.completed) == 2
    assert state.current_story.id == "story-3"
    assert state.current_story.phase == PHASE_DEV
    assert state.current_story.started_at.isoformat() == "2025-12-26T14:23:07+00:00"


def test_serialization_round_trip() -> None:
    """Test to_dict() -> from_dict() preserves data."""
    original = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/my-epic.md",
            status=STATUS_COMPLETED,
            branch="feature/my-branch",
        ),
        stories=StoriesSection(
            total=3,
            current_index=3,
            completed=[
                CompletedStory(story_id="1-1", commit="aaa111"),
                CompletedStory(story_id="1-2", commit="bbb222"),
                CompletedStory(story_id="1-3", commit="ccc333"),
            ],
        ),
        current_story=CurrentStorySection(
            id="1-3",
            phase=PHASE_REVIEW,
            iteration=2,
            started_at=datetime.now(timezone.utc),
        ),
        error=ErrorSection(type=None, message=None, phase=None),
    )

    # Serialize and deserialize
    serialized = original.to_dict()
    restored = WorkflowState.from_dict(serialized)

    # Verify all fields match
    assert restored.workflow.epic_path == original.workflow.epic_path
    assert restored.workflow.status == original.workflow.status
    assert restored.workflow.branch == original.workflow.branch
    assert restored.stories.total == original.stories.total
    assert restored.stories.current_index == original.stories.current_index
    assert len(restored.stories.completed) == len(original.stories.completed)
    assert restored.current_story.id == original.current_story.id
    assert restored.current_story.phase == original.current_story.phase
    assert restored.current_story.iteration == original.current_story.iteration


def test_atomic_write_cleans_up_temp_file(tmp_path) -> None:
    """Test atomic write cleans up temp file on success."""

    from bmad_auto.core.state import save

    state_path = tmp_path / ".bmad-auto-state.yaml"
    temp_path = state_path.with_suffix(".tmp")

    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )

    save(state, state_path)

    # Verify main file exists and temp file is cleaned up
    assert state_path.exists()
    assert not temp_path.exists()


def test_atomic_write_cleans_up_temp_file_on_failure(tmp_path) -> None:
    """Test atomic write cleans up temp file when write fails."""
    from pathlib import Path
    from unittest.mock import patch

    from bmad_auto.core.state import save

    state_path = tmp_path / ".bmad-auto-state.yaml"
    temp_path = state_path.with_suffix(".tmp")

    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )

    # Mock Path.write_text to raise an exception
    with patch.object(Path, "write_text", side_effect=OSError("Write failed")):
        try:
            save(state, state_path)
            assert False, "Expected OSError to be raised"
        except OSError:
            pass

    # Verify temp file is cleaned up even on failure
    assert not temp_path.exists()


def test_atomic_write_replaces_existing_file(tmp_path) -> None:
    """Test atomic write correctly replaces existing file."""

    from bmad_auto.core.state import load, save

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Create initial state
    state1 = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )
    save(state1, state_path)

    # Update with new state
    now = datetime.now(timezone.utc)
    state2 = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/epic-002.md",
            status=STATUS_IN_PROGRESS,
            branch="epic/epic-002",
        ),
        stories=StoriesSection(total=5, current_index=2, completed=[]),
        current_story=CurrentStorySection(
            id="story-3", phase=PHASE_DEV, iteration=1, started_at=now
        ),
        error=ErrorSection(type=None, message=None, phase=None),
    )
    save(state2, state_path)

    # Verify file contains new state
    loaded = load(state_path)
    assert loaded.workflow.epic_path == "docs/epics/epic-002.md"
    assert loaded.stories.total == 5


def test_load_detects_malformed_yaml(tmp_path) -> None:
    """Test load() detects malformed YAML."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write invalid YAML
    state_path.write_text("workflow: [invalid\nyaml: content")

    with pytest.raises(StateCorruptionError, match="corrupted or invalid YAML"):
        load(state_path)


def test_load_detects_missing_required_sections(tmp_path) -> None:
    """Test load() detects missing required sections."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write YAML missing 'stories' section
    state_path.write_text(
        """
workflow:
  epic_path: docs/epics/epic-001.md
  status: pending
  branch: epic/epic-001
current_story:
  id: story-1
  phase: sm
  iteration: 1
  started_at: 2025-12-26T14:23:07+00:00
error:
  type: null
  message: null
  phase: null
"""
    )

    with pytest.raises(StateCorruptionError, match="missing required section: stories"):
        load(state_path)


def test_load_detects_missing_workflow_fields(tmp_path) -> None:
    """Test load() detects missing workflow fields."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write YAML missing 'status' field in workflow
    state_path.write_text(
        """
workflow:
  epic_path: docs/epics/epic-001.md
  branch: epic/epic-001
stories:
  total: 3
  current_index: 0
  completed: []
current_story:
  id: story-1
  phase: sm
  iteration: 1
  started_at: 2025-12-26T14:23:07+00:00
error:
  type: null
  message: null
  phase: null
"""
    )

    with pytest.raises(
        StateCorruptionError, match="missing required field: workflow.status"
    ):
        load(state_path)


def test_load_detects_missing_stories_fields(tmp_path) -> None:
    """Test load() detects missing stories fields."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write YAML missing 'total' field in stories
    state_path.write_text(
        """
workflow:
  epic_path: docs/epics/epic-001.md
  status: pending
  branch: epic/epic-001
stories:
  current_index: 0
  completed: []
current_story:
  id: story-1
  phase: sm
  iteration: 1
  started_at: 2025-12-26T14:23:07+00:00
error:
  type: null
  message: null
  phase: null
"""
    )

    with pytest.raises(
        StateCorruptionError, match="missing required field: stories.total"
    ):
        load(state_path)


def test_load_detects_missing_current_story_fields(tmp_path) -> None:
    """Test load() detects missing current_story fields."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write YAML missing 'phase' field in current_story
    state_path.write_text(
        """
workflow:
  epic_path: docs/epics/epic-001.md
  status: pending
  branch: epic/epic-001
stories:
  total: 3
  current_index: 0
  completed: []
current_story:
  id: story-1
  iteration: 1
  started_at: 2025-12-26T14:23:07+00:00
error:
  type: null
  message: null
  phase: null
"""
    )

    with pytest.raises(
        StateCorruptionError, match="missing required field: current_story.phase"
    ):
        load(state_path)


def test_load_detects_invalid_datetime_format(tmp_path) -> None:
    """Test load() detects invalid datetime format."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write YAML with invalid datetime
    state_path.write_text(
        """
workflow:
  epic_path: docs/epics/epic-001.md
  status: pending
  branch: epic/epic-001
stories:
  total: 3
  current_index: 0
  completed: []
current_story:
  id: story-1
  phase: sm
  iteration: 1
  started_at: not-a-valid-datetime
error:
  type: null
  message: null
  phase: null
"""
    )

    with pytest.raises(StateCorruptionError, match="contains invalid data"):
        load(state_path)


def test_load_detects_file_not_found(tmp_path) -> None:
    """Test load() raises StateCorruptionError for missing file."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Don't create the file - FileNotFoundError gets wrapped
    # in StateCorruptionError for consistent error handling
    with pytest.raises(StateCorruptionError, match="corrupted or invalid YAML"):
        load(state_path)


def test_load_state_corruption_error_has_recovery_message(tmp_path) -> None:
    """Test StateCorruptionError provides helpful recovery message."""

    from bmad_auto.core.state import load
    from bmad_auto.shared.exceptions import StateCorruptionError

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Write invalid YAML
    state_path.write_text("invalid: [yaml")

    with pytest.raises(StateCorruptionError) as exc_info:
        load(state_path)

    # Error message should include the file path
    assert str(state_path) in str(exc_info.value)


def test_default_values_for_optional_fields() -> None:
    """Test that optional fields default correctly."""
    section = ErrorSection(type=None, message=None, phase=None)

    assert section.type is None
    assert section.message is None
    assert section.phase is None


def test_completed_story_dataclass() -> None:
    """Test CompletedStory nested dataclass."""
    completed = CompletedStory(story_id="story-1", commit="abc123def456")

    assert completed.story_id == "story-1"
    assert completed.commit == "abc123def456"


# =============================================================================
# Tests for State Persistence (Story 2.3)
# =============================================================================


def test_save_state_creates_yaml_file(tmp_path) -> None:
    """Test save() creates a YAML file with state data."""

    from bmad_auto.core.state import save

    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )

    save(state, state_path)

    assert state_path.exists()
    assert state_path.is_file()


def test_save_state_creates_valid_yaml(tmp_path) -> None:
    """Test save() creates valid YAML that can be loaded."""

    import yaml

    from bmad_auto.core.state import save

    state_path = tmp_path / ".bmad-auto-state.yaml"
    state = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=3,
        branch="epic/epic-001",
    )

    save(state, state_path)

    # Verify YAML is valid and loadable
    with open(state_path) as f:
        data = yaml.safe_load(f)

    assert "workflow" in data
    assert "stories" in data
    assert "current_story" in data
    assert "error" in data


def test_load_state_reconstructs_workflow_state(tmp_path) -> None:
    """Test load() reconstructs WorkflowState accurately."""

    from bmad_auto.core.state import load, save

    state_path = tmp_path / ".bmad-auto-state.yaml"
    original = WorkflowState.new(
        epic_path="docs/epics/epic-001.md",
        story_count=5,
        branch="epic/epic-001",
    )

    save(original, state_path)
    loaded = load(state_path)

    assert loaded.workflow.epic_path == original.workflow.epic_path
    assert loaded.workflow.status == original.workflow.status
    assert loaded.workflow.branch == original.workflow.branch
    assert loaded.stories.total == original.stories.total
    assert loaded.current_story.id == original.current_story.id


def test_save_load_round_trip_preserves_all_data(tmp_path) -> None:
    """Test save() -> load() round trip preserves all state data."""

    from bmad_auto.core.state import load, save

    state_path = tmp_path / ".bmad-auto-state.yaml"

    # Create complex state with data in all sections
    now = datetime.now(timezone.utc)
    original = WorkflowState(
        workflow=WorkflowSection(
            epic_path="docs/epics/complex-epic.md",
            status=STATUS_IN_PROGRESS,
            branch="feature/complex",
        ),
        stories=StoriesSection(
            total=10,
            current_index=3,
            completed=[
                CompletedStory(story_id="1-1", commit="abc123"),
                CompletedStory(story_id="1-2", commit="def456"),
            ],
        ),
        current_story=CurrentStorySection(
            id="1-3",
            phase=PHASE_DEV,
            iteration=2,
            started_at=now,
        ),
        error=ErrorSection(type=None, message=None, phase=None),
    )

    save(original, state_path)
    restored = load(state_path)

    # Verify all sections match
    assert restored.workflow.epic_path == original.workflow.epic_path
    assert restored.workflow.status == original.workflow.status
    assert restored.stories.total == original.stories.total
    assert restored.stories.current_index == original.stories.current_index
    assert len(restored.stories.completed) == len(original.stories.completed)
    assert restored.current_story.id == original.current_story.id
    assert restored.current_story.phase == original.current_story.phase
    assert restored.current_story.iteration == original.current_story.iteration
