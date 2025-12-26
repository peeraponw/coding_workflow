"""Epic file parser for BMAD markdown format.

Parses epic files containing multiple stories in structured markdown format.
"""

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Story:
    """A single story within an epic."""

    id: str  # e.g., "1.1"
    title: str  # e.g., "User Registration"
    content: str  # Full markdown content


@dataclass(frozen=True)
class Epic:
    """A BMAD epic containing multiple stories."""

    title: str
    description: str
    stories: list[Story]

    @property
    def story_count(self) -> int:
        """Return the number of stories in this epic."""
        return len(self.stories)


class ParseError(Exception):
    """Raised when epic file parsing fails."""

    def __init__(self, message: str, line_number: int | None = None) -> None:
        """Initialize ParseError with optional line number."""
        self.line_number = line_number
        if line_number is not None:
            full_message = f"{message} (line {line_number})"
        else:
            full_message = message
        super().__init__(full_message)


# Regex patterns
EPIC_HEADER_PATTERN = re.compile(r"^#\s+Epic:\s*(.+)$", re.MULTILINE)
STORY_PATTERN = re.compile(
    r"""^
    \#{1,2}\s+                    # 1 or 2 hashes + spaces
    Story\s+                       # "Story" literal
    (\d+(?:\.\d+)*)                # Story ID (e.g., "1.1")
    :\s*                           # Colon separator
    (.+?)                          # Story title (non-greedy)
    \s*$                           # End of line
    """,
    re.MULTILINE | re.VERBOSE,
)


def parse_epic(epic_path: Path) -> Epic:
    """Parse a BMAD epic markdown file.

    Args:
        epic_path: Path to the epic markdown file.

    Returns:
        Epic object with title, description, and list of stories.

    Raises:
        ParseError: If the epic file format is invalid.
    """
    content = epic_path.read_text()
    lines = content.split("\n")

    # Find epic header
    epic_header_match = EPIC_HEADER_PATTERN.search(content)
    if not epic_header_match:
        raise ParseError("No epic header found (expected '# Epic: Title')", line_number=1)

    epic_title = epic_header_match.group(1).strip()
    header_end_pos = epic_header_match.end()

    # Extract description (content between epic header and first story)
    story_matches = list(STORY_PATTERN.finditer(content))

    if not story_matches:
        raise ParseError(
            "No stories found in epic file (expected '# Story N.N: Title')",
            line_number=_find_line_number(lines, header_end_pos),
        )

    # Get description from after epic header to first story
    first_story_start = story_matches[0].start()
    description = content[header_end_pos:first_story_start].strip()

    # Parse stories
    stories: list[Story] = []

    for i, story_match in enumerate(story_matches):
        story_id = story_match.group(1)
        story_title = story_match.group(2).strip()
        story_start = story_match.end()

        # Story content goes from end of this story header to start of next story (or EOF)
        if i + 1 < len(story_matches):
            story_end = story_matches[i + 1].start()
        else:
            story_end = len(content)

        story_content = content[story_start:story_end].strip()

        stories.append(Story(id=story_id, title=story_title, content=story_content))

    return Epic(title=epic_title, description=description, stories=stories)


def _find_line_number(lines: list[str], position: int) -> int:
    """Find the line number for a given character position.

    Args:
        lines: List of content lines.
        position: Character position in the original content.

    Returns:
        1-based line number containing the position.
    """
    current_pos = 0
    for line_num, line in enumerate(lines, start=1):
        current_pos += len(line) + 1  # +1 for newline
        if current_pos > position:
            return line_num
    return len(lines)
