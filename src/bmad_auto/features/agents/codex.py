"""Codex CLI agent wrapper."""

from __future__ import annotations

import json
from typing import Sequence

from bmad_auto.features.agents.base import BaseAgent
from bmad_auto.features.agents.models import AgentConfig, AgentResult


class CodexAgent(BaseAgent):
    """Executes prompts via the `codex` CLI."""

    def __init__(self, config: AgentConfig) -> None:
        super().__init__(config)
        self._binary = "codex"

    def build_command(self, prompt: str, session_id: str | None) -> Sequence[str]:
        cmd: list[str] = [
            self._binary,
            "exec",
            "--json",
        ]
        if self.config.settings_file:
            cmd.extend(["--config", str(self.config.settings_file)])
        if session_id:
            cmd.extend(["resume", "--last"])
        else:
            cmd.append(prompt)
        cmd.extend(self.config.extra_args)
        return cmd

    def parse_output(self, raw_output: str) -> AgentResult:
        # Codex emits JSONL; parse the last non-empty line
        lines = [line for line in raw_output.splitlines() if line.strip()]
        if not lines:
            raise json.JSONDecodeError("Empty output", raw_output, 0)
        last = json.loads(lines[-1])
        agent_msg = last.get("agent_message") or {}
        return AgentResult(
            success=last.get("event") == "task.completed",
            output=agent_msg.get("text", ""),
            error=agent_msg.get("error"),
            session_id=agent_msg.get("session_id"),
            cost_usd=agent_msg.get("cost_usd"),
            duration_seconds=0.0,
        )


__all__ = ["CodexAgent"]
