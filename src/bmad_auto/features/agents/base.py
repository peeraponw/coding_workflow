"""Abstract base class for CLI agents."""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence

from bmad_auto.core.exceptions import (
    AgentExecutionError,
    AgentNotFoundError,
    AgentOutputParseError,
    AgentTimeoutError,
)
from bmad_auto.features.agents.models import AgentConfig, AgentResult


class BaseAgent(ABC):
    """Shared subprocess execution logic for CLI-based agents."""

    def __init__(self, config: AgentConfig) -> None:
        self.config = config
        self._binary = config.cli

    def validate(self) -> None:
        """Ensure the CLI binary is available in PATH."""
        if shutil.which(self._binary) is None:
            raise AgentNotFoundError(f"CLI tool '{self._binary}' not found in PATH")

    async def run(self, prompt: str, session_id: str | None = None) -> AgentResult:
        """Execute the agent prompt asynchronously with timeout handling."""
        self.validate()
        cmd = self.build_command(prompt=prompt, session_id=session_id)
        start = time.monotonic()
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.config.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.config.timeout)
            except asyncio.TimeoutError as exc:  # pragma: no cover - branch tested via exception
                process.kill()
                raise AgentTimeoutError(f"Agent timed out after {self.config.timeout}s") from exc

        except OSError as exc:  # pragma: no cover - rare, but explicit
            raise AgentExecutionError(str(exc)) from exc

        duration = time.monotonic() - start
        if process.returncode != 0:
            raise AgentExecutionError(stderr.decode().strip() or f"exit code {process.returncode}")

        try:
            result = self.parse_output(stdout.decode())
        except json.JSONDecodeError as exc:  # pragma: no cover - explicit
            raise AgentOutputParseError(str(exc)) from exc

        result.duration_seconds = duration
        return result

    @abstractmethod
    def build_command(self, prompt: str, session_id: str | None) -> Sequence[str]:
        """Construct the CLI command for the given prompt."""

    @abstractmethod
    def parse_output(self, raw_output: str) -> AgentResult:
        """Parse raw stdout into an AgentResult instance."""


__all__ = ["BaseAgent"]
