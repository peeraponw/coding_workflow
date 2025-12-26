# Story 4.3: Agent Handoff Logging

Status: ready-for-dev

## Story

As a **user**,
I want **to see when agents hand off to each other**,
so that **I understand the workflow progression**.

## Acceptance Criteria

1. **Given** SM completes and hands off to Dev, **When** the handoff occurs, **Then** log shows (FR21): `[14:25:12] HANDOFF: SM → Dev (story ready for implementation)`
2. **Given** Dev completes and hands off to Reviewer, **When** the handoff occurs, **Then** log shows: `[14:32:45] HANDOFF: Dev → Reviewer (code ready for review)`
3. **Given** Reviewer rejects and hands back to Dev, **When** the handoff occurs, **Then** log shows: `[14:35:22] HANDOFF: Reviewer → Dev (revision needed: missing error handling)`
4. **Given** Reviewer approves, **When** the approval occurs, **Then** log shows: `[14:38:15] REVIEW: Approved - proceeding to commit`
5. Handoff reasons are concise but informative
6. Tests verify handoff log format

## Tasks / Subtasks

- [ ] Task 1: Implement handoff logging functions (AC: 1-4)
  - [ ] `log_handoff(from_agent, to_agent, reason)`
  - [ ] `log_review_approved()`
  - [ ] Format with arrow notation
- [ ] Task 2: Integrate with orchestrator (AC: 1-4)
  - [ ] Call log_handoff at each phase transition
  - [ ] Include appropriate reason message
- [ ] Task 3: Implement reason messages (AC: 5)
  - [ ] SM → Dev: "story ready for implementation"
  - [ ] Dev → Reviewer: "code ready for review"
  - [ ] Reviewer → Dev: Extract reason from review feedback
  - [ ] Reviewer approval: "Approved - proceeding to commit"
- [ ] Task 4: Write tests (AC: 6)
  - [ ] Test each handoff log format
  - [ ] Test reason inclusion
  - [ ] Test arrow formatting

## Dev Notes

### Architecture Patterns & Constraints

- Handoff logs are user-facing (use Rich console)
- Include structlog entry for debugging
- Reasons should be concise (under 50 chars)
- Arrow notation for visual clarity

### Handoff Log Format

```python
def log_handoff(from_agent: str, to_agent: str, reason: str):
    """Log agent handoff with reason."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(
        f"[dim][{timestamp}][/dim] [cyan]HANDOFF:[/cyan] "
        f"[{AGENT_COLORS[from_agent]}]{from_agent}[/] → "
        f"[{AGENT_COLORS[to_agent]}]{to_agent}[/] "
        f"[dim]({reason})[/dim]"
    )
    # Also log to structlog for debugging
    logger.info("agent_handoff", from_agent=from_agent, to_agent=to_agent, reason=reason)
```

### Handoff Reasons

| Transition | Reason |
|------------|--------|
| SM → Dev | "story ready for implementation" |
| Dev → Reviewer | "code ready for review" |
| Reviewer → Dev | "revision needed: {first_issue}" |
| Reviewer ✓ | "Approved - proceeding to commit" |

### Source Tree Components

```
src/bmad_auto/
├── shared/
│   └── logging.py      # Add log_handoff function
└── core/
    └── orchestrator.py # Call log_handoff at transitions
```

### Testing Standards

- Capture console output for testing
- Verify arrow formatting
- Test reason truncation

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-4-progress-monitoring-logging.md#story-43-agent-handoff-logging]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#agent-orchestration]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
