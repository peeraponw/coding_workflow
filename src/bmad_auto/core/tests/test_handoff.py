"""Tests for handoff file management."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from bmad_auto.core.handoff import (
    HANDOFF_DIR,
    SmToDevHandoff,
    DevToReviewerHandoff,
    ReviewerToDevHandoff,
    create_sm_to_dev_handoff,
    create_dev_to_reviewer_handoff,
    create_reviewer_to_dev_handoff,
    cleanup_handoffs,
)


@pytest.fixture
def temp_handoff_dir(tmp_path: Path) -> Path:
    """Create a temporary handoff directory."""
    import bmad_auto.core.handoff as handoff_module

    original_dir = handoff_module.HANDOFF_DIR
    handoff_module.HANDOFF_DIR = tmp_path / ".bmad-auto" / "handoffs"
    handoff_module._get_datetime.cache_clear()

    yield handoff_module.HANDOFF_DIR

    handoff_module.HANDOFF_DIR = original_dir
    handoff_module._get_datetime.cache_clear()


class TestSmToDevHandoff:
    """Test SM → Dev handoff file creation."""

    def test_creates_handoff_file(self, temp_handoff_dir) -> None:
        """Should create handoff file in correct location."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            story_content="As a developer...",
            acceptance_criteria=["AC1", "AC2"],
        )

        path = create_sm_to_dev_handoff(handoff)

        assert path.parent == temp_handoff_dir / "3-1"
        assert path.name == "sm_to_dev.yaml"
        assert path.exists()

    def test_includes_story_data(self, temp_handoff_dir) -> None:
        """Should include story content and acceptance criteria."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            story_content="As a developer, I want a protocol",
            acceptance_criteria=[
                "Given agents module, when import, then accessible",
                "Given protocol, when implemented, when compliant",
            ],
        )

        path = create_sm_to_dev_handoff(handoff)

        content = yaml.safe_load(path.read_text())
        assert content["story"]["id"] == "3-1"
        assert content["story"]["title"] == "Agent Protocol"
        assert "As a developer" in content["story"]["content"]
        assert len(content["acceptance_criteria"]) == 2

    def test_includes_context_fields_when_provided(self, temp_handoff_dir) -> None:
        """Should include context notes and constraints when provided."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            story_content="Content",
            acceptance_criteria=["AC1"],
            context_notes="Use Protocol for duck typing",
            constraints="Must be runtime_checkable",
        )

        path = create_sm_to_dev_handoff(handoff)

        content = yaml.safe_load(path.read_text())
        assert content["context_notes"] == "Use Protocol for duck typing"
        assert content["constraints"] == "Must be runtime_checkable"

    def test_adds_human_readable_comments(self, temp_handoff_dir) -> None:
        """Should include comments for readability."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Test",
            story_content="Content",
            acceptance_criteria=["AC1"],
        )

        path = create_sm_to_dev_handoff(handoff)

        text = path.read_text()
        assert "# Handoff: SM → Dev" in text
        assert "# Story: 3-1" in text
        assert "# Generated:" in text


class TestDevToReviewerHandoff:
    """Test Dev → Reviewer handoff file creation."""

    def test_creates_handoff_file(self, temp_handoff_dir) -> None:
        """Should create handoff file in correct location."""
        handoff = DevToReviewerHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            implementation_summary="Added Protocol class",
            files_changed=["src/bmad_auto/agents/base.py"],
        )

        path = create_dev_to_reviewer_handoff(handoff)

        assert path.parent == temp_handoff_dir / "3-1"
        assert path.name == "dev_to_reviewer.yaml"
        assert path.exists()

    def test_includes_implementation_data(self, temp_handoff_dir) -> None:
        """Should include implementation summary and files changed."""
        handoff = DevToReviewerHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            implementation_summary="Implemented AgentProtocol with run method",
            files_changed=[
                "src/bmad_auto/agents/base.py",
                "src/bmad_auto/agents/__init__.py",
            ],
            diff_reference=".bmad-auto/diffs/story-3-1.diff",
        )

        path = create_dev_to_reviewer_handoff(handoff)

        content = yaml.safe_load(path.read_text())
        impl = content["implementation"]
        assert "AgentProtocol" in impl["summary"]
        assert impl["files_changed"][0] == "src/bmad_auto/agents/base.py"
        assert impl["diff_reference"] == ".bmad-auto/diffs/story-3-1.diff"

    def test_adds_human_readable_comments(self, temp_handoff_dir) -> None:
        """Should include comments for readability."""
        handoff = DevToReviewerHandoff(
            story_id="3-1",
            story_title="Test",
            implementation_summary="Summary",
            files_changed=["file.py"],
        )

        path = create_dev_to_reviewer_handoff(handoff)

        text = path.read_text()
        assert "# Handoff: Dev → Reviewer" in text
        assert "# Story: 3-1" in text


class TestReviewerToDevHandoff:
    """Test Reviewer → Dev handoff file creation."""

    def test_creates_handoff_file(self, temp_handoff_dir) -> None:
        """Should create handoff file in correct location."""
        handoff = ReviewerToDevHandoff(
            story_id="3-1",
            approved=False,
            issues=["Missing type hints"],
            suggestions=["Add type hints"],
            iteration=1,
            files_touched=["src/bmad_auto/agents/base.py"],
        )

        path = create_reviewer_to_dev_handoff(handoff)

        assert path.parent == temp_handoff_dir / "3-1"
        assert path.name == "reviewer_to_dev.yaml"
        assert path.exists()

    def test_includes_iteration_in_filename_after_first(self, temp_handoff_dir) -> None:
        """Should append _iterN to filename for iterations > 1."""
        handoff = ReviewerToDevHandoff(
            story_id="3-1",
            approved=False,
            issues=["Issue"],
            suggestions=["Fix"],
            iteration=2,
            files_touched=["file.py"],
        )

        path = create_reviewer_to_dev_handoff(handoff)

        assert path.name == "reviewer_to_dev_iter2.yaml"

    def test_includes_feedback_data(self, temp_handoff_dir) -> None:
        """Should include approval status, issues, and suggestions."""
        handoff = ReviewerToDevHandoff(
            story_id="3-1",
            approved=False,
            issues=[
                "Missing input validation",
                "No error handling for edge cases",
            ],
            suggestions=[
                "Add pydantic validation",
                "Add try/except for API calls",
            ],
            iteration=1,
            files_touched=["src/bmad_auto/agents/base.py"],
        )

        path = create_reviewer_to_dev_handoff(handoff)

        content = yaml.safe_load(path.read_text())
        feedback = content["feedback"]
        assert feedback["approved"] is False
        assert len(feedback["issues"]) == 2
        assert len(feedback["suggestions"]) == 2

        context = content["previous_context"]
        assert context["iteration"] == 1
        assert context["files_touched"][0] == "src/bmad_auto/agents/base.py"


class TestHandoffCleanup:
    """Test handoff file cleanup."""

    def test_removes_handoff_directory(self, temp_handoff_dir) -> None:
        """Should remove handoff directory and all files."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Test",
            story_content="Content",
            acceptance_criteria=["AC1"],
        )

        create_sm_to_dev_handoff(handoff)
        handoff_dir = temp_handoff_dir / "3-1"
        assert handoff_dir.exists()

        cleanup_handoffs("3-1")

        assert not handoff_dir.exists()

    def test_handles_nonexistent_directory(self, temp_handoff_dir) -> None:
        """Should not error when cleaning up non-existent directory."""
        # Should not raise
        cleanup_handoffs("nonexistent-story")


class TestHandoffHumanReadable:
    """Test handoff file human-readability (AC5)."""

    def test_yaml_is_pretty_printed(self, temp_handoff_dir) -> None:
        """YAML should be formatted for human readability."""
        handoff = SmToDevHandoff(
            story_id="3-1",
            story_title="Agent Protocol",
            story_content="As a developer, I want...",
            acceptance_criteria=[
                "Given valid input, when process, then success",
                "Given invalid input, when process, then error",
            ],
            context_notes="Use typing.Protocol",
        )

        path = create_sm_to_dev_handoff(handoff)
        text = path.read_text()

        # Check for proper YAML formatting
        assert "story:" in text
        assert "acceptance_criteria:" in text
        assert "context_notes:" in text

        # Check that lists are formatted with dashes (YAML default style)
        assert "- Given valid" in text or "- \"Given valid" in text

    def test_clear_key_names(self, temp_handoff_dir) -> None:
        """Should use readable key names (not abbreviated)."""
        handoff = DevToReviewerHandoff(
            story_id="3-1",
            story_title="Test",
            implementation_summary="Summary",
            files_changed=["file.py"],
            diff_reference="diff.ref",
        )

        path = create_dev_to_reviewer_handoff(handoff)
        content = yaml.safe_load(path.read_text())

        # Check for clear, descriptive key names
        assert "implementation" in content
        assert "files_changed" in content["implementation"]
        assert "diff_reference" in content["implementation"]

        # No abbreviations at the implementation level
        assert "impl" not in content
        assert "summary" in content["implementation"]
