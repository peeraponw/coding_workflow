# Story 4.2: Timestamped Workflow Logging

Status: ready-for-dev

## Story

As a **user**,
I want **timestamped logs showing workflow progression**,
so that **I can see what's happening and debug issues**.

## Acceptance Criteria

1. **Given** a workflow is executing, **When** any workflow event occurs, **Then** it's logged with ISO timestamp (FR20):
   ```
   [2025-12-26T14:23:07] WORKFLOW: Starting epic docs/epics/epic-001.md
   [2025-12-26T14:23:08] SM: Creating story 1 of 5...
   [2025-12-26T14:25:12] SM: Story created - "Add user authentication"
   [2025-12-26T14:25:13] DEV: Implementing story...
   ```
2. **Given** an error occurs, **When** the error is logged, **Then** timestamp and error details are included and no credentials or sensitive data appear in logs (NFR14)
3. Logs use Rich formatting with colors
4. Agent phases are color-coded (SM=blue, Dev=green, Reviewer=yellow)
5. Tests verify log format and timestamp presence

## Tasks / Subtasks

- [ ] Task 1: Extend logging module (AC: 1, 3-4)
  - [ ] Add workflow event logging functions
  - [ ] Include ISO timestamps in all log output
  - [ ] Use Rich formatting with agent colors
- [ ] Task 2: Implement workflow event loggers (AC: 1)
  - [ ] `log_workflow_start(epic_path)`
  - [ ] `log_phase_start(phase, story_num, total)`
  - [ ] `log_phase_complete(phase, details)`
  - [ ] `log_story_complete(story_id)`
- [ ] Task 3: Implement error logging (AC: 2)
  - [ ] Log errors with timestamps
  - [ ] Include error details
  - [ ] Filter sensitive data
- [ ] Task 4: Add color coding (AC: 4)
  - [ ] SM logs in blue
  - [ ] Dev logs in green
  - [ ] Reviewer logs in yellow
  - [ ] Error logs in red
- [ ] Task 5: Write tests (AC: 5)
  - [ ] Test timestamp format
  - [ ] Test color coding
  - [ ] Test no sensitive data leakage

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Never log credentials or API keys (NFR14)
- Use Rich console for all output
- ISO 8601 timestamp format
- Consistent prefix format: `[timestamp] AGENT: message`

### Log Format Pattern

```python
def log_phase(agent: str, message: str):
    """Log phase event with timestamp and color."""
    timestamp = datetime.now().isoformat(timespec='seconds')
    color = AGENT_COLORS.get(agent, "white")
    console.print(f"[dim][{timestamp}][/dim] [{color}]{agent}:[/{color}] {message}")
```

### Agent Colors

```python
AGENT_COLORS = {
    "WORKFLOW": "cyan",
    "SM": "blue",
    "DEV": "green",
    "REVIEWER": "yellow",
    "ERROR": "red",
    "GIT": "magenta",
}
```

### Sensitive Data Filtering

```python
SENSITIVE_PATTERNS = [
    r"ANTHROPIC_API_KEY=\S+",
    r"api[_-]?key[=:]\S+",
    r"token[=:]\S+",
]

def sanitize_log(message: str) -> str:
    """Remove sensitive data from log messages."""
    for pattern in SENSITIVE_PATTERNS:
        message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)
    return message
```

### Source Tree Components

```
src/bmad_auto/shared/
├── logging.py        # Extend with workflow logging
└── tests/
    └── test_logging.py
```

### Testing Standards

- Capture Rich output for testing
- Verify timestamp format
- Test sensitive data filtering

### References

- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#logging-pattern-per-agentsmd-8]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#logging-strategy]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
