"""Pydantic models for workflow state persistence."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class WorkflowState(BaseModel):
    """Top-level persisted workflow state."""

    workflow_id: str
    epic_file: str
    status: Literal["pending", "running", "paused", "failed", "completed"]
    branch_name: str | None = None
    branch_created: bool = False
    current_phase: str
    current_story: str | None = None
    completed_stories: list[str] = Field(default_factory=list)
    failed_stories: list[str] = Field(default_factory=list)
    error: str | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("epic_file")
    @classmethod
    def _epic_path_str(cls, value: str) -> str:
        # Normalize to POSIX style for portability
        return str(Path(value))

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)


class StoryContext(BaseModel):
    """State associated with the current story execution."""

    story_id: str
    story_file: str
    dev_attempts: int = 0
    review_passed: bool = False


__all__ = ["WorkflowState", "StoryContext"]
