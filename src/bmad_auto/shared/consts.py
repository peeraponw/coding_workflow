"""Shared constants for bmad-auto.

All constants MUST live in this file - no magic numbers/strings elsewhere.
"""

from typing import Final

# Exit codes
EXIT_SUCCESS: Final[int] = 0
EXIT_ERROR: Final[int] = 1
EXIT_PAUSED: Final[int] = 2
EXIT_CONFIG_ERROR: Final[int] = 3

# Agents
AGENT_SM: Final[str] = "sm"
AGENT_DEV: Final[str] = "dev"
AGENT_REVIEWER: Final[str] = "reviewer"

# Phases
PHASE_SM: Final[str] = "sm"
PHASE_DEV: Final[str] = "dev"
PHASE_REVIEW: Final[str] = "review"

# Status
STATUS_PENDING: Final[str] = "pending"
STATUS_IN_PROGRESS: Final[str] = "in-progress"
STATUS_PAUSED: Final[str] = "paused"
STATUS_COMPLETED: Final[str] = "completed"
STATUS_FAILED: Final[str] = "failed"

# Error Types
ERROR_RATE_LIMIT: Final[str] = "rate_limit"
ERROR_API: Final[str] = "api_error"
ERROR_UNEXPECTED: Final[str] = "unexpected"
