"""Claude Code CLI agent wrapper."""

from __future__ import annotations

import json
from typing import Sequence

from bmad_auto.features.agents.base import BaseAgent
from bmad_auto.features.agents.models import AgentConfig, AgentResult


class ClaudeAgent(BaseAgent):
    """Executes prompts via the `claude` CLI."""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(config)
        self._binary = "claude"

    def build_command(self, prompt: str, session_id: str | None) -> Sequence[str]:
        cmd: list[str] = [self._binary, "-p", prompt, "--output-format", "json"]
        if self.config.settings_file:
            cmd.extend(["--settings", str(self.config.settings_file)])
        if session_id:
            cmd.extend(["--resume", session_id])
        cmd.extend(self.config.extra_args)
        return cmd

    def parse_output(self, raw_output: str) -> AgentResult:
        data = json.loads(raw_output)
        return AgentResult(
            success=data.get("result") == "success",
            output=data.get("output", ""),
            error=data.get("error"),
            session_id=data.get("session_id"),
            cost_usd=data.get("total_cost_usd"),
            duration_seconds=0.0,  # filled in by BaseAgent
        )


__all__ = ["ClaudeAgent"]
