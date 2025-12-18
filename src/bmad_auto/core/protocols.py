"""Protocol interfaces used for dependency injection."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class AgentProtocol(Protocol):
    """Interface for CLI agent wrappers."""

    async def run(self, prompt: str, session_id: str | None = None):
        """Execute an agent prompt and return an AgentResult."""

    def validate(self) -> None:
        """Validate that the agent can be executed in the current environment."""


@runtime_checkable
class StateManagerProtocol(Protocol):
    """Interface for workflow state persistence."""

    def load(self, workflow_id: str):
        """Load a workflow state by identifier."""

    def save(self, state):
        """Persist the provided workflow state."""

    def list_all(self):
        """Return all known workflow states."""


@runtime_checkable
class GitManagerProtocol(Protocol):
    """Interface for git operations."""

    def create_branch(self, name: str) -> None:
        """Create a new branch from the current HEAD."""

    def commit(self, message: str) -> None:
        """Create a commit with staged changes."""

    def push_and_create_pr(self, title: str, body: str) -> str:
        """Push the branch and create a pull request, returning the PR URL."""


@runtime_checkable
class ProgressReporterProtocol(Protocol):
    """Interface for reporting workflow progress to a UI."""

    def on_phase_start(self, phase: str, story_id: str | None) -> None:
        """Notify that a workflow phase is beginning."""

    def on_agent_start(self, role: str) -> None:
        """Notify that an agent run is starting."""

    def on_complete(self, success: bool) -> None:
        """Notify that the workflow has completed."""
