# Story 4.1: Status Command Implementation

Status: ready-for-dev

## Story

As a **user**,
I want **to check workflow status without interrupting execution**,
so that **I can monitor progress while AFK**.

## Acceptance Criteria

1. **Given** a workflow is in progress, **When** I run `bmad-auto status` in another terminal, **Then** I see: Epic path, Status: IN_PROGRESS, Progress (Story X of Y), Current Story details (title, phase, iteration, started time, duration), Completed Stories with commit references (FR17)
2. **Given** no workflow is in progress, **When** I run `bmad-auto status`, **Then** I see: "No active workflow. Run 'bmad-auto run --epic <file>' to start."
3. **Given** workflow is paused due to error, **When** I run `bmad-auto status`, **Then** I see status: PAUSED with error details and resume instructions
4. Status command reads state file without locking (non-blocking)
5. Tests verify all status display scenarios

## Tasks / Subtasks

- [ ] Task 1: Implement full status command (AC: 1)
  - [ ] Update stub from Story 1.4
  - [ ] Read state file
  - [ ] Format status output with Rich
  - [ ] Show epic path, overall status, progress
  - [ ] Show current story details
  - [ ] Show completed stories with commits
- [ ] Task 2: Implement no-workflow case (AC: 2)
  - [ ] Check if state file exists
  - [ ] Display helpful message if not
- [ ] Task 3: Implement paused status display (AC: 3)
  - [ ] Detect paused status
  - [ ] Show error details
  - [ ] Show resume instructions
- [ ] Task 4: Ensure non-blocking reads (AC: 4)
  - [ ] Read file without locking
  - [ ] Handle concurrent access gracefully
- [ ] Task 5: Write tests (AC: 5)
  - [ ] Test in-progress display
  - [ ] Test no-workflow display
  - [ ] Test paused display
  - [ ] Test output formatting

## Dev Notes

### Architecture Patterns & Constraints

- Status command is READ-ONLY - never modifies state
- Use Rich for formatted output
- Non-blocking file read (no locks)
- Calculate duration from started_at timestamp

### Status Output Format

```
Epic: docs/epics/epic-001.md
Status: IN_PROGRESS
Progress: Story 3 of 5

Current Story: "Add user validation"
  Phase: review (iteration 2)
  Started: 14:23:07
  Duration: 12m 34s

Completed Stories:
  ✓ Story 1: "Setup project" - committed (abc123)
  ✓ Story 2: "Add models" - committed (def456)
```

### Color Coding

```python
# Status colors
STATUS_COLORS = {
    STATUS_IN_PROGRESS: "green",
    STATUS_PAUSED: "yellow",
    STATUS_COMPLETED: "blue",
    STATUS_FAILED: "red",
}
```

### Source Tree Components

```
src/bmad_auto/
├── main.py           # Status command implementation
└── core/
    └── display.py    # Status formatting utilities (optional)
```

### Testing Standards

- Mock state file for tests
- Test Rich output capture
- Verify all display scenarios

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-4-progress-monitoring-logging.md#story-41-status-command-implementation]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#logging-strategy]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
