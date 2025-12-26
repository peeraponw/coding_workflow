"""Shared module for bmad-auto.

This module provides constants, types, and exceptions used across all other modules.
"""

# Export exit codes
from bmad_auto.shared.consts import (
    EXIT_CONFIG_ERROR,
    EXIT_ERROR,
    EXIT_PAUSED,
    EXIT_SUCCESS,
)

# Export agent constants
from bmad_auto.shared.consts import (
    AGENT_DEV,
    AGENT_REVIEWER,
    AGENT_SM,
)

# Export phase constants
from bmad_auto.shared.consts import (
    PHASE_DEV,
    PHASE_REVIEW,
    PHASE_SM,
)

# Export status constants
from bmad_auto.shared.consts import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_PAUSED,
    STATUS_PENDING,
)

# Export types
from bmad_auto.shared.types import (
    AgentId,
    EpicKey,
    EpicPath,
    Phase,
    StoryId,
    StoryKey,
    StoryStatus,
    WorkflowState,
)

# Export exceptions
from bmad_auto.shared.exceptions import (
    AgentError,
    BmadAutoError,
    ConfigError,
    StateCorruptionError,
    WorkflowPausedError,
)

__all__ = [
    # Exit codes
    "EXIT_SUCCESS",
    "EXIT_ERROR",
    "EXIT_PAUSED",
    "EXIT_CONFIG_ERROR",
    # Agents
    "AGENT_SM",
    "AGENT_DEV",
    "AGENT_REVIEWER",
    # Phases
    "PHASE_SM",
    "PHASE_DEV",
    "PHASE_REVIEW",
    # Status
    "STATUS_PENDING",
    "STATUS_IN_PROGRESS",
    "STATUS_PAUSED",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    # Types
    "StoryId",
    "StoryKey",
    "EpicKey",
    "EpicPath",
    "AgentId",
    "Phase",
    "StoryStatus",
    "WorkflowState",
    # Exceptions
    "BmadAutoError",
    "ConfigError",
    "StateCorruptionError",
    "AgentError",
    "WorkflowPausedError",
]
