"""Tests for epic file parser."""

import pytest

from bmad_auto.core.parser import Epic, ParseError, Story, parse_epic


def test_valid_epic_parsing(tmp_path) -> None:
    """Test parsing a valid epic file with all components."""
    epic_content = """# Epic: User Authentication

This epic handles user authentication flows
including registration, login, and session management.

## Story 1.1: User Registration

As a user,
I want to register with email and password,
so that I can access the system.

### Acceptance Criteria

1. Email validation works
2. Password strength enforced

## Story 1.2: User Login

As a user,
I want to login with credentials,
so that I can access my account.

### Acceptance Criteria

1. Invalid login shows error
2. Session created on success
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    result = parse_epic(epic_file)

    assert result.title == "User Authentication"
    assert "user authentication flows" in result.description.lower()
    assert result.story_count == 2

    # First story
    story1 = result.stories[0]
    assert story1.id == "1.1"
    assert story1.title == "User Registration"
    assert "register with email" in story1.content.lower()

    # Second story
    story2 = result.stories[1]
    assert story2.id == "1.2"
    assert story2.title == "User Login"
    assert "login with credentials" in story2.content.lower()


def test_malformed_epic_no_header(tmp_path) -> None:
    """Test parsing fails when epic header is missing."""
    epic_content = """## Story 1.1: Some Story

Content here.
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    with pytest.raises(ParseError) as exc_info:
        parse_epic(epic_file)

    assert "epic header" in str(exc_info.value).lower()
    assert "line 1" in str(exc_info.value).lower() or "line 0" in str(exc_info.value).lower()


def test_malformed_epic_no_stories(tmp_path) -> None:
    """Test parsing fails when no stories are found."""
    epic_content = """# Epic: Empty Epic

This epic has no stories.
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    with pytest.raises(ParseError) as exc_info:
        parse_epic(epic_file)

    assert "no stories" in str(exc_info.value).lower() or "stories" in str(exc_info.value).lower()


def test_edge_case_empty_story_content(tmp_path) -> None:
    """Test handling stories with minimal content."""
    epic_content = """# Epic: Minimal Epic

Description.

## Story 1.1: Empty Story

"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    result = parse_epic(epic_file)

    assert result.story_count == 1
    assert result.stories[0].id == "1.1"
    assert result.stories[0].title == "Empty Story"
    assert result.stories[0].content == ""


def test_edge_case_missing_description(tmp_path) -> None:
    """Test handling epic with no description between header and first story."""
    epic_content = """# Epic: No Description

## Story 1.1: First Story

Story content.
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    result = parse_epic(epic_file)

    assert result.title == "No Description"
    assert result.description == ""
    assert result.story_count == 1


def test_various_markdown_heading_styles(tmp_path) -> None:
    """Test parsing different markdown heading styles for stories."""
    epic_content = """# Epic: Heading Styles

Description text.

# Story 1.1: Hash Style

Content for hash style.

## Story 1.2: Double Hash Style

Content for double hash.
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    result = parse_epic(epic_file)

    assert result.story_count == 2
    assert result.stories[0].id == "1.1"
    assert result.stories[0].title == "Hash Style"
    assert result.stories[1].id == "1.2"
    assert result.stories[1].title == "Double Hash Style"


def test_story_dataclass_properties() -> None:
    """Test Story dataclass structure."""
    story = Story(id="2.3", title="Test Story", content="Story content here")

    assert story.id == "2.3"
    assert story.title == "Test Story"
    assert story.content == "Story content here"


def test_epic_dataclass_story_count() -> None:
    """Test Epic dataclass story_count property."""
    stories = [
        Story(id="1.1", title="Story 1", content="Content 1"),
        Story(id="1.2", title="Story 2", content="Content 2"),
        Story(id="1.3", title="Story 3", content="Content 3"),
    ]

    epic = Epic(title="Test Epic", description="Test description", stories=stories)

    assert epic.story_count == 3


def test_parse_error_includes_line_numbers(tmp_path) -> None:
    """Test that ParseError includes line numbers for debugging."""
    epic_content = """Invalid content line 1
Invalid content line 2
Invalid content line 3
"""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(epic_content)

    with pytest.raises(ParseError) as exc_info:
        parse_epic(epic_file)

    error_msg = str(exc_info.value).lower()
    # Should include line number reference
    assert "line" in error_msg
