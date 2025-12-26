"""Agent protocol and base implementations.

This module provides:
- AgentProtocol: Structural typing for agent invocation
- AgentResult: Result type for agent execution
- AgentRole: Enum of agent roles
- ClaudeAgent: Claude Agent SDK adapter
- Command builders: build_sm_command, build_dev_command, build_reviewer_command
- Agent factory: create_agent for model routing
"""

from bmad_auto.agents.base import AgentProtocol, AgentResult, AgentRole
from bmad_auto.agents.claude import ClaudeAgent
from bmad_auto.agents.factory import create_agent
from bmad_auto.agents.prompts import (
    build_sm_command,
    build_dev_command,
    build_reviewer_command,
)

__all__ = [
    "AgentProtocol",
    "AgentResult",
    "AgentRole",
    "ClaudeAgent",
    "create_agent",
    "build_sm_command",
    "build_dev_command",
    "build_reviewer_command",
]
