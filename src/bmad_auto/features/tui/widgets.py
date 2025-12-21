"""Textual widgets for the bmad-auto TUI."""

from __future__ import annotations

from textual.widgets import DataTable, RichLog, Static


class WorkflowStatusWidget(Static):
    """Display the current workflow phase and story."""

    def update_status(self, phase: str, story_id: str | None, agent: str | None = None) -> None:
        story_text = story_id or "-"
        agent_text = agent or "-"
        self.update(f"Phase: {phase}\nStory: {story_text}\nAgent: {agent_text}")


class StoryTableWidget(DataTable):
    """Render story progress in a table."""

    def __init__(self) -> None:
        super().__init__()
        self.add_column("Story")
        self.add_column("Status")
        self._rows: dict[str, int] = {}

    def set_stories(self, stories: list[str]) -> None:
        self.clear()
        self._rows.clear()
        for story in stories:
            row_key = self.add_row(story, "pending")
            self._rows[story] = row_key

    def update_story(self, story_id: str, status: str) -> None:
        row_key = self._rows.get(story_id)
        if row_key is None:
            return
        self.update_cell(row_key, 1, status)


class AgentLogWidget(RichLog):
    """Streaming log area for agent and phase events."""

    def log_event(self, message: str) -> None:
        self.write(message)


class ControlsWidget(Static):
    """Display keybindings."""

    def __init__(self) -> None:
        super().__init__("q: quit")


__all__ = [
    "AgentLogWidget",
    "ControlsWidget",
    "StoryTableWidget",
    "WorkflowStatusWidget",
]
