"""Tests for shared type aliases."""


from bmad_auto.shared.types import (
    AgentId,
    EpicKey,
    EpicPath,
    Phase,
    StoryId,
    StoryKey,
    StoryStatus,
    WorkflowState,
)


class TestStoryId:
    """Test StoryId type alias."""

    def test_story_id_is_str(self) -> None:
        """StoryId should be a string type alias."""
        story_id: StoryId = "1-2-user-auth"
        assert isinstance(story_id, str)


class TestStoryKey:
    """Test StoryKey type alias."""

    def test_story_key_is_str(self) -> None:
        """StoryKey should be a string type alias."""
        story_key: StoryKey = "1-2-user-auth"
        assert isinstance(story_key, str)


class TestEpicKey:
    """Test EpicKey type alias."""

    def test_epic_key_is_str(self) -> None:
        """EpicKey should be a string type alias."""
        epic_key: EpicKey = "epic-1"
        assert isinstance(epic_key, str)


class TestEpicPath:
    """Test EpicPath type alias."""

    def test_epic_path_is_str(self) -> None:
        """EpicPath should be a string type alias (file path)."""
        epic_path: EpicPath = "_bmad-output/epics/epic-1.md"
        assert isinstance(epic_path, str)


class TestAgentId:
    """Test AgentId type alias."""

    def test_agent_id_is_str(self) -> None:
        """AgentId should be a string type alias."""
        agent_id: AgentId = "sm"
        assert isinstance(agent_id, str)


class TestPhase:
    """Test Phase type alias."""

    def test_phase_is_str(self) -> None:
        """Phase should be a string type alias."""
        phase: Phase = "sm"
        assert isinstance(phase, str)


class TestStoryStatus:
    """Test StoryStatus type alias."""

    def test_story_status_is_str(self) -> None:
        """StoryStatus should be a string type alias."""
        status: StoryStatus = "in-progress"
        assert isinstance(status, str)


class TestWorkflowState:
    """Test WorkflowState type alias."""

    def test_workflow_state_is_dict(self) -> None:
        """WorkflowState should be a dict type alias."""
        state: WorkflowState = {"current_epic": "epic-1", "current_story": "1-1-test"}
        assert isinstance(state, dict)
