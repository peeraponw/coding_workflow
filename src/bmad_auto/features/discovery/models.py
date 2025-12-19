"""Pydantic models for epic and story metadata extraction."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class EpicInfo(BaseModel):
    """Structured information parsed from an epic markdown file."""

    id: str
    title: str
    description: str
    story_refs: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    file_path: Path

    @field_validator("file_path", mode="before")
    @classmethod
    def _coerce_path(cls, value: str | Path) -> Path:
        return Path(value)


class StoryInfo(BaseModel):
    """Structured information parsed from a story markdown file."""

    id: str
    title: str
    context: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    file_path: Path

    @field_validator("file_path", mode="before")
    @classmethod
    def _coerce_path(cls, value: str | Path) -> Path:
        return Path(value)


__all__ = ["EpicInfo", "StoryInfo"]
