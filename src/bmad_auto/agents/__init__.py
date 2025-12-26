"""Agent protocol and base implementations.

This module provides:
- AgentProtocol: Structural typing for agent invocation
- AgentResult: Result type for agent execution
- AgentRole: Enum of agent roles
"""

from bmad_auto.agents.base import AgentProtocol, AgentResult, AgentRole

__all__ = ["AgentProtocol", "AgentResult", "AgentRole"]
