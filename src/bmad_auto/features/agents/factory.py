"""Factory to create agent instances from configuration."""

from __future__ import annotations

from bmad_auto.core.exceptions import AgentNotFoundError
from bmad_auto.features.agents.claude import ClaudeAgent
from bmad_auto.features.agents.codex import CodexAgent
from bmad_auto.features.agents.models import AgentConfig


def create_agent(config: AgentConfig):
    """Instantiate an agent based on the configured CLI value."""
    if config.cli == "claude":
        return ClaudeAgent(config)
    if config.cli == "codex":
        return CodexAgent(config)
    raise AgentNotFoundError(f"Unsupported CLI '{config.cli}'")


__all__ = ["create_agent"]
