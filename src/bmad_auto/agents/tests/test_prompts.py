"""Tests for agent command builders."""


from bmad_auto.agents.prompts import (
    build_sm_command,
    build_dev_command,
    build_reviewer_command,
)


class TestBuildSmCommand:
    """Test SM command builder."""

    def test_builds_command_with_story_index(self) -> None:
        """Should include story index in command."""
        result = build_sm_command(1)
        assert result == "/bmad:bmm:agents:sm create story 1 from epic"

    def test_handles_different_story_indices(self) -> None:
        """Should handle various story indices."""
        assert build_sm_command(1) == "/bmad:bmm:agents:sm create story 1 from epic"
        assert build_sm_command(5) == "/bmad:bmm:agents:sm create story 5 from epic"
        assert build_sm_command(10) == "/bmad:bmm:agents:sm create story 10 from epic"


class TestBuildDevCommand:
    """Test Dev command builder."""

    def test_builds_command_with_story_file(self) -> None:
        """Should include story file path in command."""
        result = build_dev_command("story-3-1.md")
        assert result == "/bmad:bmm:workflows:dev-story story-3-1.md"

    def test_handles_different_file_names(self) -> None:
        """Should handle various story file names."""
        assert build_dev_command("story-1.md") == "/bmad:bmm:workflows:dev-story story-1.md"
        assert build_dev_command("3-5-story-loop.md") == "/bmad:bmm:workflows:dev-story 3-5-story-loop.md"


class TestBuildReviewerCommand:
    """Test Reviewer command builder."""

    def test_builds_command_with_story_file(self) -> None:
        """Should include story file path in command."""
        result = build_reviewer_command("story-3-1.md")
        assert result == "/bmad:bmm:workflows:code-review story-3-1.md"

    def test_handles_different_file_names(self) -> None:
        """Should handle various story file names."""
        assert (
            build_reviewer_command("story-1.md")
            == "/bmad:bmm:workflows:code-review story-1.md"
        )
        assert (
            build_reviewer_command("3-5-story-loop.md")
            == "/bmad:bmm:workflows:code-review 3-5-story-loop.md"
        )


class TestCommandFormatConsistency:
    """Test that all commands follow bmad skill format."""

    def test_all_commands_use_skill_prefix(self) -> None:
        """All commands should start with /bmad:bmm: prefix."""
        sm_cmd = build_sm_command(1)
        dev_cmd = build_dev_command("story.md")
        reviewer_cmd = build_reviewer_command("story.md")

        assert sm_cmd.startswith("/bmad:bmm:")
        assert dev_cmd.startswith("/bmad:bmm:")
        assert reviewer_cmd.startswith("/bmad:bmm:")

    def test_commands_contain_no_prompt_text(self) -> None:
        """Commands should be skill invocations, not raw prompts."""
        # No "you are" or other prompt language
        sm_cmd = build_sm_command(1)
        dev_cmd = build_dev_command("story.md")
        reviewer_cmd = build_reviewer_command("story.md")

        assert "you are" not in sm_cmd.lower()
        assert "you are" not in dev_cmd.lower()
        assert "you are" not in reviewer_cmd.lower()
