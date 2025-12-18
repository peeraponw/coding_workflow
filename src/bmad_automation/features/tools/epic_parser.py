"""Markdown epic file parser."""

import re
from pathlib import Path

from pydantic import BaseModel

from bmad_automation.shared.exceptions import EpicParseError


class StoryOutline(BaseModel):
    """A story extracted from an epic."""

    id: str
    title: str
    description: str


class Epic(BaseModel):
    """Parsed epic with stories."""

    id: str
    title: str
    description: str
    stories: list[StoryOutline]


def parse_epic_file(epic_path: Path) -> Epic:
    """Parse a markdown epic file into structured data."""
    if not epic_path.exists():
        raise EpicParseError(f"Epic file not found: {epic_path}")

    content = epic_path.read_text()

    epic_match = re.search(r"^# Epic:\s*(.+)$", content, re.MULTILINE)
    if not epic_match:
        raise EpicParseError("Epic title not found. Expected: # Epic: <title>")

    epic_title = epic_match.group(1).strip()
    epic_id = epic_path.stem.lower().replace(" ", "-")

    desc_match = re.search(r"^# Epic:.+?\n\n(.+?)(?=\n## Stories)", content, re.DOTALL)
    epic_desc = desc_match.group(1).strip() if desc_match else ""

    stories: list[StoryOutline] = []
    story_pattern = r"### Story (\d+):\s*(.+?)\n\n(.+?)(?=\n### Story|\Z)"
    for match in re.finditer(story_pattern, content, re.DOTALL):
        stories.append(
            StoryOutline(
                id=f"{epic_id}-story-{match.group(1)}",
                title=match.group(2).strip(),
                description=match.group(3).strip(),
            )
        )

    return Epic(id=epic_id, title=epic_title, description=epic_desc, stories=stories)
