"""Shared constants for bmad-auto.

All constants MUST live in this file - no magic numbers/strings elsewhere.
"""

# Exit codes
EXIT_SUCCESS: int = 0
EXIT_ERROR: int = 1
EXIT_PAUSED: int = 2
EXIT_CONFIG_ERROR: int = 3

# Agents
AGENT_SM: str = "sm"
AGENT_DEV: str = "dev"
AGENT_REVIEWER: str = "reviewer"

# Phases
PHASE_SM: str = "sm"
PHASE_DEV: str = "dev"
PHASE_REVIEW: str = "review"

# Status
STATUS_PENDING: str = "pending"
STATUS_IN_PROGRESS: str = "in-progress"
STATUS_PAUSED: str = "paused"
STATUS_COMPLETED: str = "completed"
STATUS_FAILED: str = "failed"
