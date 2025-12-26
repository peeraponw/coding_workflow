"""Agent command builders for skill-based invocation.

Provides pure functions that construct bmad skill command strings
for SM, Dev, and Reviewer agents.
"""


def build_sm_command(story_index: int) -> str:
    """Build SM agent command for story creation.

    Args:
        story_index: The 1-based index of the story in the epic

    Returns:
        Skill command string for SM agent

    Example:
        >>> build_sm_command(1)
        '/bmad:bmm:agents:sm create story 1 from epic'
    """
    return f"/bmad:bmm:agents:sm create story {story_index} from epic"


def build_dev_command(story_file: str) -> str:
    """Build Dev agent command for story implementation.

    Args:
        story_file: Path to the story file to implement

    Returns:
        Skill command string for Dev agent

    Example:
        >>> build_dev_command("story-3-1.md")
        '/bmad:bmm:workflows:dev-story story-3-1.md'
    """
    return f"/bmad:bmm:workflows:dev-story {story_file}"


def build_reviewer_command(story_file: str) -> str:
    """Build Reviewer agent command for code review.

    Args:
        story_file: Path to the story file to review

    Returns:
        Skill command string for Reviewer agent

    Example:
        >>> build_reviewer_command("story-3-1.md")
        '/bmad:bmm:workflows:code-review story-3-1.md'
    """
    return f"/bmad:bmm:workflows:code-review {story_file}"
