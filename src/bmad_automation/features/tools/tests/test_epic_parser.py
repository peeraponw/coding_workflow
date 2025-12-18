"""Tests for epic parser."""

from pathlib import Path

import pytest

from bmad_automation.features.tools.epic_parser import parse_epic_file
from bmad_automation.shared.exceptions import EpicParseError


def test_parse_epic_extracts_stories(tmp_path: Path) -> None:
    """Test that epic parser extracts stories correctly."""
    epic_file = tmp_path / "test-epic.md"
    epic_file.write_text("""# Epic: User Auth

Implement authentication.

## Stories

### Story 1: Login

Users can log in.

### Story 2: Logout

Users can log out.
""")
    epic = parse_epic_file(epic_file)
    assert epic.title == "User Auth"
    assert epic.id == "test-epic"
    assert len(epic.stories) == 2
    assert epic.stories[0].title == "Login"
    assert epic.stories[1].title == "Logout"


def test_parse_epic_fails_on_missing_file(tmp_path: Path) -> None:
    """Test that parser raises error on missing file."""
    with pytest.raises(EpicParseError, match="not found"):
        parse_epic_file(tmp_path / "missing.md")


def test_parse_epic_fails_on_missing_title(tmp_path: Path) -> None:
    """Test that parser raises error on missing epic title."""
    epic_file = tmp_path / "bad-epic.md"
    epic_file.write_text("# Some other content")
    with pytest.raises(EpicParseError, match="Epic title not found"):
        parse_epic_file(epic_file)
