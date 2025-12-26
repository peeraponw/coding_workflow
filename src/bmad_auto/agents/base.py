"""Agent protocol and result types.

Provides structural typing for agent invocation and result handling.
All agents receive prompts and return AgentResult.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Protocol, runtime_checkable

from bmad_auto.shared.consts import AGENT_DEV, AGENT_REVIEWER, AGENT_SM


class AgentRole(Enum):
    """Agent role identifiers.

    Links to AGENT_* constants from shared/consts.py for consistency.
    """

    SM = AGENT_SM
    DEV = AGENT_DEV
    REVIEWER = AGENT_REVIEWER


@dataclass(frozen=True)
class AgentResult:
    """Immutable result from agent execution.

    Attributes:
        success: True if execution completed without errors
        output: Agent output text (present on both success and failure)
        error: Optional error message (present only on failure)
    """

    success: bool
    output: str
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate result state."""
        if self.success and self.error:
            raise ValueError("Successful result cannot have error message")
        if not self.success and not self.error:
            raise ValueError("Failed result must have error message")

    @classmethod
    def ok(cls, output: str) -> "AgentResult":
        """Create successful result.

        Args:
            output: Agent output text

        Returns:
            AgentResult with success=True
        """
        return cls(success=True, output=output)

    @classmethod
    def fail(cls, error: str, output: str = "") -> "AgentResult":
        """Create failed result.

        Args:
            error: Error message
            output: Optional partial output

        Returns:
            AgentResult with success=False
        """
        return cls(success=False, output=output, error=error)


@runtime_checkable
class AgentProtocol(Protocol):
    """Structural typing for agent invocation.

    All agents must implement async run(command: str) -> AgentResult.
    Uses Protocol for duck typing with type hints.
    """

    async def run(self, command: str) -> AgentResult:
        """Execute agent command and return result.

        Args:
            command: Agent command/prompt

        Returns:
            AgentResult with success status and output
        """
        ...
