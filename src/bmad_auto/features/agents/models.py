"""Pydantic models for agent configuration and results."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from bmad_auto.shared.consts import DEFAULT_AGENT_TIMEOUT


class AgentConfig(BaseModel):
    """Configuration for an individual agent invocation."""

    cli: Literal["claude", "codex"]
    settings_file: Path | None = Field(default=None, description="Path to CLI settings file")
    working_dir: Path = Field(default=Path("."), description="Working directory for the CLI call")
    timeout: int = Field(default=DEFAULT_AGENT_TIMEOUT, description="Timeout in seconds")
    extra_args: list[str] = Field(default_factory=list, description="Additional CLI arguments")


class AgentResult(BaseModel):
    """Result object returned by agent executions."""

    success: bool
    output: str
    error: str | None = None
    session_id: str | None = None
    cost_usd: float | None = None
    duration_seconds: float


__all__ = ["AgentConfig", "AgentResult"]
