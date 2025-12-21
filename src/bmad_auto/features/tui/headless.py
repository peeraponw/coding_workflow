"""Headless progress reporter for CLI mode."""

from __future__ import annotations

from datetime import datetime, timezone

from rich.console import Console

from bmad_auto.core.protocols import ProgressReporterProtocol


class HeadlessReporter(ProgressReporterProtocol):
    """Rich-based reporter for non-TUI workflows."""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console(highlight=False)

    def on_phase_start(self, phase: str, story_id: str | None) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        story = f" ({story_id})" if story_id else ""
        self._console.log(f"[{timestamp}] phase: {phase}{story}")

    def on_agent_start(self, role: str) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        self._console.log(f"[{timestamp}] agent: {role}")

    def on_complete(self, success: bool) -> None:
        status = "success" if success else "failed"
        self._console.log(f"workflow {status}")


__all__ = ["HeadlessReporter"]
