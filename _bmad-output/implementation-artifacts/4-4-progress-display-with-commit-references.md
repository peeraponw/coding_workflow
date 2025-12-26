# Story 4.4: Progress Display with Commit References

Status: complete

## Story

As a **user**,
I want **to see completed stories with their commit hashes**,
so that **I can verify what's been done and review commits**.

## Acceptance Criteria

1. **Given** stories have been completed and committed, **When** I view status or logs, **Then** I see commit references (FR18, FR19):
   ```
   Completed Stories:
     ✓ Story 1: "Setup project structure" - committed (a1b2c3d)
     ✓ Story 2: "Add user model" - committed (e4f5g6h)
     ✓ Story 3: "Implement registration" - committed (i7j8k9l)
   ```
2. **Given** a story is in progress, **When** I view status, **Then** I see current phase and iteration:
   ```
   Current Story: "Add login endpoint"
     Phase: dev
     Iteration: 1
     Started: 14:45:22
   ```
3. **Given** workflow completes successfully, **When** I view final status, **Then** I see summary:
   ```
   Epic: docs/epics/epic-001.md
   Status: COMPLETED
   Total Stories: 5
   Total Commits: 5
   Branch: epic/epic-001
   Duration: 45m 12s
   ```
4. Commit hashes are in short format (7 chars)
5. Tests verify progress display formatting

## Tasks / Subtasks

- [x] Task 1: Implement completed stories display (AC: 1)
  - [x] Read completed stories from state
  - [x] Format with checkmark and commit hash
  - [x] Use short commit hash format (7 chars)
- [x] Task 2: Implement current story display (AC: 2)
  - [x] Show story title
  - [x] Show current phase
  - [x] Show iteration count
  - [x] Show started time
  - [x] Calculate and show duration
- [x] Task 3: Implement completion summary (AC: 3)
  - [x] Detect completed status
  - [x] Show total stories and commits
  - [x] Show branch name
  - [x] Calculate total duration
- [x] Task 4: Format commit hashes (AC: 4)
  - [x] Truncate to 7 characters
  - [x] Handle missing commit gracefully
- [x] Task 5: Write tests (AC: 5)
  - [x] Test completed stories format
  - [x] Test current story format
  - [x] Test completion summary
  - [x] Test commit hash formatting

### Review Follow-ups (AI)

- [ ] [AI-Review][LOW] Verify test directories have __init__.py files for pytest discovery [src/bmad_auto/core/tests/]

## Dev Notes

### Architecture Patterns & Constraints

- Read from WorkflowState completed stories list
- Short commit hashes (7 chars) for display
- Use Rich for formatted output
- Duration calculated from timestamps

### Display Formatting

```python
def display_completed_stories(state: WorkflowState):
    """Display completed stories with commit references."""
    console.print("\n[bold]Completed Stories:[/bold]")
    for story in state.stories.completed:
        short_hash = story.commit[:7] if story.commit else "pending"
        console.print(
            f"  [green]✓[/green] {story.story_id} - committed ({short_hash})"
        )

def display_current_story(state: WorkflowState):
    """Display current story progress."""
    cs = state.current_story
    duration = calculate_duration(cs.started_at)
    console.print(f"\n[bold]Current Story:[/bold] \"{cs.id}\"")
    console.print(f"  Phase: {cs.phase}")
    console.print(f"  Iteration: {cs.iteration}")
    console.print(f"  Started: {format_time(cs.started_at)}")
    console.print(f"  Duration: {duration}")
```

### Duration Calculation

```python
def calculate_duration(started_at: str) -> str:
    """Calculate human-readable duration from ISO timestamp."""
    start = datetime.fromisoformat(started_at)
    delta = datetime.now() - start
    minutes = int(delta.total_seconds() // 60)
    seconds = int(delta.total_seconds() % 60)
    return f"{minutes}m {seconds}s"
```

### Source Tree Components

```
src/bmad_auto/
├── main.py           # Status command uses display functions
└── core/
    └── display.py    # Progress display utilities
```

### Testing Standards

- Test with mock state data
- Verify Rich output formatting
- Test edge cases (no commits, long durations)

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-4-progress-monitoring-logging.md#story-44-progress-display-with-commit-references]
- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#state-file-format]

## Dev Agent Record

### Agent Model Used
claude-opus-4-5-20251101

### Debug Log References
None - implementation was already covered by Story 4.1 display.py module.

### Completion Notes List
- Progress display functions already implemented in display.py from Story 4.1
- Added additional tests for commit hash formatting (7 chars)
- Added tests for missing commit handling (shows "pending")
- All acceptance criteria met:
  - AC1: Completed stories display with commit references (short hash format)
  - AC2: Current story shows title, phase, iteration, started time
  - AC3: Completion summary shows total stories, commits, branch, duration
  - AC4: Commit hashes truncated to 7 characters
  - AC5: Progress display formatting tested

### File List
- `src/bmad_auto/core/display.py` (already existed from 4.1)
- `src/bmad_auto/core/tests/test_display.py` (modified - added more tests)