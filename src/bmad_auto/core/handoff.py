"""Handoff file management for agent context passing.

Creates YAML handoff files to pass context between agents (SM → Dev → Reviewer).
Files are human-readable for debugging and stored in .bmad-auto/handoffs/.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import yaml

# Handoff directory
HANDOFF_DIR: Path = Path(".bmad-auto/handoffs")


@dataclass(frozen=True)
class SmToDevHandoff:
    """Handoff from SM agent to Dev agent."""

    story_id: str
    story_title: str
    story_content: str
    acceptance_criteria: list[str]
    context_notes: str | None = None
    constraints: str | None = None


@dataclass(frozen=True)
class DevToReviewerHandoff:
    """Handoff from Dev agent to Reviewer agent."""

    story_id: str
    story_title: str
    implementation_summary: str
    files_changed: list[str]
    diff_reference: str | None = None


@dataclass(frozen=True)
class ReviewerToDevHandoff:
    """Handoff from Reviewer agent back to Dev agent (for iterations)."""

    story_id: str
    approved: bool
    issues: list[str]
    suggestions: list[str]
    iteration: int
    files_touched: list[str]


def _get_handoff_dir(story_id: str) -> Path:
    """Get handoff directory for a specific story.

    Args:
        story_id: Story ID (e.g., "3-1")

    Returns:
        Path to handoff directory for the story
    """
    return HANDOFF_DIR / story_id


def _ensure_handoff_dir(story_id: str) -> Path:
    """Ensure handoff directory exists for a story.

    Args:
        story_id: Story ID

    Returns:
        Path to handoff directory
    """
    handoff_dir = _get_handoff_dir(story_id)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    return handoff_dir


@lru_cache(maxsize=1)
def _get_datetime() -> datetime:
    """Get current datetime (cached for handoff consistency).

    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def _write_yaml_comment(file, comment: str) -> None:
    """Write a YAML comment line to a file.

    Args:
        file: File object to write to
        comment: Comment text (without # prefix)
    """
    file.write(f"# {comment}\n")


def create_sm_to_dev_handoff(handoff: SmToDevHandoff) -> Path:
    """Create SM → Dev handoff file.

    Args:
        handoff: Handoff data to write

    Returns:
        Path to created handoff file
    """
    handoff_dir = _ensure_handoff_dir(handoff.story_id)
    handoff_path = handoff_dir / "sm_to_dev.yaml"

    data = {
        "story": {
            "id": handoff.story_id,
            "title": handoff.story_title,
            "content": handoff.story_content,
        },
        "acceptance_criteria": handoff.acceptance_criteria,
    }

    if handoff.context_notes:
        data["context_notes"] = handoff.context_notes
    if handoff.constraints:
        data["constraints"] = handoff.constraints

    with open(handoff_path, "w") as f:
        _write_yaml_comment(f, "Handoff: SM → Dev")
        _write_yaml_comment(f, f"Story: {handoff.story_id}")
        _write_yaml_comment(f, f"Generated: {_get_datetime().isoformat()}")
        _write_yaml_comment(f, "")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return handoff_path


def create_dev_to_reviewer_handoff(handoff: DevToReviewerHandoff) -> Path:
    """Create Dev → Reviewer handoff file.

    Args:
        handoff: Handoff data to write

    Returns:
        Path to created handoff file
    """
    handoff_dir = _ensure_handoff_dir(handoff.story_id)
    handoff_path = handoff_dir / "dev_to_reviewer.yaml"

    data = {
        "story": {
            "id": handoff.story_id,
            "title": handoff.story_title,
        },
        "implementation": {
            "summary": handoff.implementation_summary,
            "files_changed": handoff.files_changed,
        },
    }

    if handoff.diff_reference:
        data["implementation"]["diff_reference"] = handoff.diff_reference

    with open(handoff_path, "w") as f:
        _write_yaml_comment(f, "Handoff: Dev → Reviewer")
        _write_yaml_comment(f, f"Story: {handoff.story_id}")
        _write_yaml_comment(f, f"Generated: {_get_datetime().isoformat()}")
        _write_yaml_comment(f, "")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return handoff_path


def create_reviewer_to_dev_handoff(handoff: ReviewerToDevHandoff) -> Path:
    """Create Reviewer → Dev handoff file (for review iterations).

    Args:
        handoff: Handoff data to write

    Returns:
        Path to created handoff file
    """
    handoff_dir = _ensure_handoff_dir(handoff.story_id)
    iter_suffix = f"_iter{handoff.iteration}" if handoff.iteration > 1 else ""
    handoff_path = handoff_dir / f"reviewer_to_dev{iter_suffix}.yaml"

    data = {
        "feedback": {
            "approved": handoff.approved,
            "issues": handoff.issues,
            "suggestions": handoff.suggestions,
        },
        "previous_context": {
            "iteration": handoff.iteration,
            "files_touched": handoff.files_touched,
        },
    }

    with open(handoff_path, "w") as f:
        _write_yaml_comment(f, "Handoff: Reviewer → Dev")
        if handoff.iteration > 1:
            _write_yaml_comment(f, f"Iteration: {handoff.iteration}")
        _write_yaml_comment(f, f"Story: {handoff.story_id}")
        _write_yaml_comment(f, f"Generated: {_get_datetime().isoformat()}")
        _write_yaml_comment(f, "")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return handoff_path


def cleanup_handoffs(story_id: str) -> None:
    """Clean up handoff files for a completed story.

    Args:
        story_id: Story ID whose handoffs should be cleaned up
    """
    handoff_dir = _get_handoff_dir(story_id)
    if handoff_dir.exists():
        for file in handoff_dir.iterdir():
            file.unlink()
        handoff_dir.rmdir()
