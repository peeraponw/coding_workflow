"""Textual application for tracking workflow progress."""

from __future__ import annotations

import asyncio
import queue
import threading
from dataclasses import dataclass
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header

from bmad_auto.core.exceptions import WorkflowError
from bmad_auto.core.protocols import ProgressReporterProtocol
from bmad_auto.features.discovery.epic_parser import EpicParser
from bmad_auto.features.orchestrator.engine import WorkflowEngine, parse_story_ref
from bmad_auto.features.tui.widgets import (
    AgentLogWidget,
    ControlsWidget,
    StoryTableWidget,
    WorkflowStatusWidget,
)


@dataclass(frozen=True)
class TuiEvent:
    """Event emitted by the workflow reporter."""

    kind: str
    phase: str | None = None
    story_id: str | None = None
    role: str | None = None
    success: bool | None = None
    message: str | None = None


class TuiReporter(ProgressReporterProtocol):
    """Reporter that pushes progress events into a queue."""

    def __init__(self, event_queue: queue.Queue[TuiEvent]) -> None:
        self._queue = event_queue

    def on_phase_start(self, phase: str, story_id: str | None) -> None:
        self._queue.put(TuiEvent(kind="phase", phase=phase, story_id=story_id))

    def on_agent_start(self, role: str) -> None:
        self._queue.put(TuiEvent(kind="agent", role=role))

    def on_complete(self, success: bool) -> None:
        self._queue.put(TuiEvent(kind="complete", success=success))


class WorkflowApp(App[None]):
    """Run a workflow and visualize progress in a Textual UI."""

    BINDINGS = [("q", "quit", "Quit")]

    def __init__(
        self,
        *,
        engine: WorkflowEngine | None,
        epic_path: Path,
        resume_workflow_id: str | None = None,
    ) -> None:
        super().__init__()
        self._engine: WorkflowEngine | None = engine
        self._epic_path = epic_path
        self._resume_workflow_id = resume_workflow_id
        self._event_queue: queue.Queue[TuiEvent] = queue.Queue()
        self._reporter = TuiReporter(self._event_queue)
        self._error: Exception | None = None
        self._current_phase: str = "starting"
        self._status = WorkflowStatusWidget()
        self._story_table = StoryTableWidget()
        self._agent_log = AgentLogWidget()
        self._controls = ControlsWidget()

    @property
    def reporter(self) -> ProgressReporterProtocol:
        """Expose the reporter for wiring into the workflow engine."""
        return self._reporter

    @property
    def error(self) -> Exception | None:
        """Return the workflow error, if any."""
        return self._error

    @property
    def engine(self) -> WorkflowEngine | None:
        """Return the workflow engine instance."""
        return self._engine

    @engine.setter
    def engine(self, engine: WorkflowEngine) -> None:
        """Attach the workflow engine before running the UI."""
        self._engine = engine

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            with Horizontal():
                yield self._status
                yield self._story_table
            yield self._agent_log
            yield self._controls
        yield Footer()

    def on_mount(self) -> None:
        epic = EpicParser().parse(self._epic_path)
        stories = [parse_story_ref(ref)[0] for ref in epic.story_refs]
        self._story_table.set_stories(stories)
        self._status.update_status(self._current_phase, None, None)
        self.set_interval(0.2, self._drain_events)
        self._start_worker()

    def _start_worker(self) -> None:
        thread = threading.Thread(target=self._run_workflow, daemon=True)
        thread.start()

    def _run_workflow(self) -> None:
        if self._engine is None:
            self._error = WorkflowError("Workflow engine not configured")
            self._event_queue.put(TuiEvent(kind="complete", success=False))
            return
        try:
            if self._resume_workflow_id:
                asyncio.run(self._engine.resume_workflow(self._resume_workflow_id))
            else:
                asyncio.run(self._engine.run_epic(self._epic_path))
        except Exception as exc:  # pragma: no cover - thread boundary
            self._error = exc
            self._event_queue.put(TuiEvent(kind="complete", success=False, message=str(exc)))
            return
        self._event_queue.put(TuiEvent(kind="complete", success=True))

    def _drain_events(self) -> None:
        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                break
            if event.kind == "phase":
                phase = event.phase or "-"
                self._current_phase = phase
                self._status.update_status(self._current_phase, event.story_id, None)
                if event.story_id:
                    self._story_table.update_story(event.story_id, phase)
                self._agent_log.log_event(f"phase: {phase}")
            elif event.kind == "agent":
                role = event.role or "-"
                self._status.update_status(self._current_phase, None, role)
                self._agent_log.log_event(f"agent: {role}")
            elif event.kind == "complete":
                if event.success:
                    self._current_phase = "completed"
                    self._status.update_status(self._current_phase, None, None)
                else:
                    message = event.message or "workflow failed"
                    self._current_phase = "failed"
                    self._status.update_status(self._current_phase, None, None)
                    self._agent_log.log_event(message)
                self.exit()
            else:
                raise WorkflowError(f"Unknown TUI event: {event.kind}")


__all__ = ["WorkflowApp", "TuiReporter"]
