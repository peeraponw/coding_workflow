# Story 4.1: Status Command Implementation

Status: done

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

- [x] Task 1: Implement full status command (AC: 1)
  - [x] Update stub from Story 1.4
  - [x] Read state file
  - [x] Format status output with Rich
  - [x] Show epic path, overall status, progress
  - [x] Show current story details
  - [x] Show completed stories with commits
- [x] Task 2: Implement no-workflow case (AC: 2)
  - [x] Check if state file exists
  - [x] Display helpful message if not
- [x] Task 3: Implement paused status display (AC: 3)
  - [x] Detect paused status
  - [x] Show error details
  - [x] Show resume instructions
- [x] Task 4: Ensure non-blocking reads (AC: 4)
  - [x] Read file without locking
  - [x] Handle concurrent access gracefully
- [x] Task 5: Write tests (AC: 5)
  - [x] Test in-progress display
  - [x] Test no-workflow display
  - [x] Test paused display
  - [x] Test output formatting

### Review Follow-ups (AI)

- [ ] [AI-Review][MEDIUM] Fix display_completion_summary duration calculation - currently uses current_story.started_at instead of workflow start time [src/bmad_auto/core/display.py:174-176]
- [ ] [AI-Review][LOW] Replace typer.echo() with rich.console.print() for Rich markup rendering in run command warning [src/bmad_auto/main.py:62-70]
- [ ] [AI-Review][LOW] Add integration tests for status command display scenarios in test_main.py

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
claude-opus-4-5-20251101

### Debug Log References
None - implementation proceeded smoothly without issues.

### Completion Notes List
- Created `src/bmad_auto/core/display.py` module for status display functions
- Updated `src/bmad_auto/main.py` status() command to use display module
- Implemented non-blocking state file reading for status command
- Added Rich-formatted output with color-coded statuses
- All acceptance criteria met:
  - AC1: Full status display with epic path, status, progress, current story, completed stories
  - AC2: No-workflow case displays helpful message
  - AC3: Paused status shows error details and resume instructions
  - AC4: Status command reads state without locking (non-blocking)
  - AC5: All display scenarios tested

### File List
- `src/bmad_auto/core/display.py` (new file)
- `src/bmad_auto/core/tests/test_display.py` (new file)
- `src/bmad_auto/main.py` (modified)
- `src/bmad_auto/tests/test_main.py` (modified tests)