"""Agent protocol and base implementations.

This module provides:
- AgentProtocol: Structural typing for agent invocation
- AgentResult: Result type for agent execution
- AgentRole: Enum of agent roles
- ClaudeAgent: Claude Agent SDK adapter
"""

from bmad_auto.agents.base import AgentProtocol, AgentResult, AgentRole
from bmad_auto.agents.claude import ClaudeAgent

__all__ = ["AgentProtocol", "AgentResult", "AgentRole", "ClaudeAgent"]
