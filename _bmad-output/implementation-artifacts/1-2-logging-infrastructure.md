# Story 1.2: Logging Infrastructure

Status: ready-for-dev

## Story

As a **developer**,
I want **structured logging with structlog and Rich console output**,
so that **logs are machine-parseable and user output is readable**.

## Acceptance Criteria

1. **Given** the shared module exists, **When** I import logging utilities from `bmad_auto.shared.logging`, **Then** I can get a structlog logger with `get_logger(__name__)`
2. **Given** the shared module exists, **When** I import logging utilities, **Then** I can access a Rich Console instance for user-facing output
3. **Given** the logging module is configured, **When** I log with `logger.info("message", key=value)`, **Then** context is properly attached
4. Log output includes timestamps
5. Rich console supports color-coded agent phases (SM=blue, Dev=green, Reviewer=yellow)
6. Tests verify logging configuration works correctly

## Tasks / Subtasks

- [ ] Task 1: Create logging module (AC: 1-3)
  - [ ] Create `src/bmad_auto/shared/logging.py`
  - [ ] Implement `get_logger(name: str)` function returning structlog logger
  - [ ] Configure structlog with timestamp processor
- [ ] Task 2: Set up Rich console (AC: 2, 5)
  - [ ] Create shared Console instance
  - [ ] Define color constants for agent phases (SM_COLOR, DEV_COLOR, REVIEWER_COLOR)
  - [ ] Create helper functions for agent-colored output
- [ ] Task 3: Configure timestamp formatting (AC: 4)
  - [ ] Add ISO timestamp to structlog output
  - [ ] Ensure timestamps appear in both log and console output
- [ ] Task 4: Export from shared module (AC: 1-2)
  - [ ] Update `shared/__init__.py` to export logging utilities
- [ ] Task 5: Write tests (AC: 6)
  - [ ] Test logger creation
  - [ ] Test structured logging with context
  - [ ] Test console output formatting

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Use structlog for logging (machine-parseable), Rich for display (human-readable)
- Never use `print()` for output - always structlog or Rich console
- Logging is a cross-cutting concern used by ALL modules
- Must NOT log credentials or sensitive data (NFR14)

### Implementation Pattern

```python
# Logging (structlog) - for debugging/auditing
import structlog
logger = structlog.get_logger(__name__)
logger.info("Agent handoff", from_agent=AGENT_SM, to_agent=AGENT_DEV)

# Display (Rich) - for user-facing output
from rich.console import Console
console = Console()
console.print("[blue]SM:[/blue] Creating story 1 of 5...")
```

### Color Coding

| Agent | Color |
|-------|-------|
| SM | Blue |
| Dev | Green |
| Reviewer | Yellow |

### Source Tree Components

```
src/bmad_auto/shared/
├── __init__.py      # Re-export get_logger, console
└── logging.py       # structlog setup, Rich console
```

### Testing Standards

- Test logger creation and basic logging
- Verify timestamp format
- Test color output (may need to capture Rich output)

### References

- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#logging-pattern-per-agentsmd-8]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#logging-strategy]
- [Source: _bmad-output/project-context.md#logging-vs-display]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
