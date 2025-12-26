# Story 1.2: Logging Infrastructure

Status: review

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

- [x] Task 1: Create logging module (AC: 1-3)
  - [x] Create `src/bmad_auto/shared/logging.py`
  - [x] Implement `get_logger(name: str)` function returning structlog logger
  - [x] Configure structlog with timestamp processor
- [x] Task 2: Set up Rich console (AC: 2, 5)
  - [x] Create shared Console instance
  - [x] Define color constants for agent phases (SM_COLOR, DEV_COLOR, REVIEWER_COLOR)
  - [x] Create helper functions for agent-colored output
- [x] Task 3: Configure timestamp formatting (AC: 4)
  - [x] Add ISO timestamp to structlog output
  - [x] Ensure timestamps appear in both log and console output
- [x] Task 4: Export from shared module (AC: 1-2)
  - [x] Update `shared/__init__.py` to export logging utilities
- [x] Task 5: Write tests (AC: 6)
  - [x] Test logger creation
  - [x] Test structured logging with context
  - [x] Test console output formatting

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

claude-opus-4-5-20251101

### Debug Log References

No debugging issues encountered.

### Completion Notes List

**Implementation Summary:**
- Created `src/bmad_auto/shared/logging.py` with structlog configuration and Rich console
- Implemented `get_logger(name: str)` function returning configured structlog logger
- Added `_add_timestamp` processor for ISO timestamps in all log entries
- Created shared `console` instance (Rich Console) for user-facing output
- Defined color constants: SM_COLOR="blue", DEV_COLOR="green", REVIEWER_COLOR="yellow"
- Implemented helper functions: `print_sm()`, `print_dev()`, `print_reviewer()` for colored output
- Exported all logging utilities from `shared/__init__.py`

**Technical Decisions:**
- Used structlog v25+ with EventDict type annotation for type safety
- Timestamps added as ISO format strings via custom processor
- Rich console with markup tags for color-coded agent output
- Helper functions follow pattern from Dev Notes: `[color]AgentName:[/color] message`

**Test Coverage:**
- 7 tests added in `test_logging.py`
- All 44 shared module tests pass
- Tests cover: logger creation, structured logging, timestamps, console, colors, print functions

### File List

- `pyproject.toml` (added rich dependency)
- `src/bmad_auto/shared/logging.py` (created)
- `src/bmad_auto/shared/__init__.py` (modified - added logging exports)
- `src/bmad_auto/shared/tests/test_logging.py` (created)

### Change Log

- 2025-12-26: Implemented logging infrastructure with structlog and Rich console
- Added `rich` dependency to pyproject.toml
- Created logging module with get_logger, console, color constants, and print functions
- Exported logging utilities from shared module
- Added comprehensive test coverage for all logging functionality
