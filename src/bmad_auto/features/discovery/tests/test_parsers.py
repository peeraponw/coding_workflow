from pathlib import Path

import pytest

from bmad_auto.core.exceptions import EpicNotFoundError, StoryCreationError
from bmad_auto.features.discovery.epic_parser import EpicParser
from bmad_auto.features.discovery.story_parser import StoryParser


def test_epic_parser_extracts_sections(tmp_path: Path) -> None:
    epic_md = """# Epic 001 - Authentication

This epic delivers secure login.

## Stories
- STORY-001: Implement login form
- STORY-002: Add password reset

## Dependencies
- platform-auth
"""
    epic_file = tmp_path / "epic-001.md"
    epic_file.write_text(epic_md)

    result = EpicParser().parse(epic_file)

    assert result.id == "epic-001"
    assert result.title == "Epic 001 - Authentication"
    assert "secure login" in result.description
    assert result.story_refs == [
        "STORY-001: Implement login form",
        "STORY-002: Add password reset",
    ]
    assert result.dependencies == ["platform-auth"]


def test_epic_parser_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(EpicNotFoundError):
        EpicParser().parse(tmp_path / "missing.md")


def test_story_parser_extracts_sections(tmp_path: Path) -> None:
    story_md = """# STORY-001 Implement login

## Context
Users need to sign in with email and password.

## Acceptance Criteria
- Given valid credentials, user sees dashboard
- Given invalid credentials, user sees error

## Checklist
- [ ] Add form
- [ ] Validate credentials
"""
    story_file = tmp_path / "story-001.md"
    story_file.write_text(story_md)

    result = StoryParser().parse(story_file)

    assert result.id == "STORY-001"
    assert result.title == "Implement login"
    assert "email and password" in result.context
    assert len(result.acceptance_criteria) == 2
    assert result.checklist == ["Add form", "Validate credentials"]


def test_story_parser_requires_id_and_title(tmp_path: Path) -> None:
    story_md = """# InvalidTitleOnly
"""
    story_file = tmp_path / "story-invalid.md"
    story_file.write_text(story_md)
    with pytest.raises(StoryCreationError):
        StoryParser().parse(story_file)
