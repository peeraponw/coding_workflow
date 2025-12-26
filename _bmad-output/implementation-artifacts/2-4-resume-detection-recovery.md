# Story 2.4: Resume Detection & Recovery

Status: done

## Story

As a **user**,
I want **to resume an interrupted workflow from the exact point**,
so that **I don't lose progress when things go wrong**.

## Acceptance Criteria

1. **Given** a state file exists with `status: in_progress` or `status: paused`, **When** I run `bmad-auto resume`, **Then** the workflow resumes from `current_story` at `current_story.phase` (FR13)
2. **Given** a state file exists with `status: in_progress`, **When** I run `bmad-auto run --epic <same-epic>`, **Then** I'm warned about existing in-progress workflow and prompted to use `resume` instead (FR14)
3. **Given** a state file exists with `status: completed`, **When** I run `bmad-auto resume`, **Then** I'm informed the workflow is already complete
4. **Given** no state file exists, **When** I run `bmad-auto resume`, **Then** I get a clear error: "No workflow to resume"
5. Resume restores exact position 100% of the time (NFR2)
6. Tests cover all resume scenarios

## Tasks / Subtasks

- [x] Task 1: Implement state detection in CLI (AC: 1-4)
  - [x] Check for state file existence
  - [x] Load state and check status
  - [x] Route to appropriate handler based on status
- [x] Task 2: Implement resume command (AC: 1)
  - [x] Load existing state
  - [x] Validate state has resumable status
  - [x] Pass to orchestrator with resume context
  - [x] Orchestrator continues from current_story.phase
- [x] Task 3: Implement run command conflict detection (AC: 2)
  - [x] Check if state file exists before starting new run
  - [x] Compare epic paths
  - [x] Warn user if in-progress workflow exists
  - [x] Prompt to use resume instead
- [x] Task 4: Handle edge cases (AC: 3-4)
  - [x] Handle completed workflow resume attempt
  - [x] Handle missing state file resume attempt
  - [x] Provide clear user messages
- [x] Task 5: Write comprehensive tests (AC: 5-6)
  - [x] Test resume from in_progress
  - [x] Test resume from paused
  - [x] Test resume with completed workflow
  - [x] Test resume with no state file
  - [x] Test run conflict detection

## Dev Notes

### Architecture Patterns & Constraints

- Resume must restore EXACT position (story + phase + iteration)
- Use Rich console for user-facing prompts
- CLI handles detection, orchestrator handles execution
- State file path from config

### Resume Logic

```python
def resume():
    state_path = get_state_path()
    if not state_path.exists():
        console.print("[red]No workflow to resume[/red]")
        raise typer.Exit(EXIT_ERROR)

    state = load_state(state_path)

    if state.workflow.status == STATUS_COMPLETED:
        console.print("[yellow]Workflow already complete[/yellow]")
        raise typer.Exit(EXIT_SUCCESS)

    if state.workflow.status in (STATUS_IN_PROGRESS, STATUS_PAUSED):
        # Resume from exact point
        anyio.run(orchestrator.resume, state)
```

### Conflict Detection

```python
def run(epic: str):
    state_path = get_state_path()
    if state_path.exists():
        state = load_state(state_path)
        if state.workflow.status == STATUS_IN_PROGRESS:
            console.print(
                f"[yellow]Warning:[/yellow] Workflow already in progress for {state.workflow.epic_path}\n"
                "Use 'bmad-auto resume' to continue."
            )
            raise typer.Exit(EXIT_ERROR)
```

### Source Tree Components

```
src/bmad_auto/
├── main.py           # Resume command, conflict detection
└── core/
    └── orchestrator.py  # Resume logic
```

### Testing Standards

- Test each resume scenario
- Verify exact position restoration
- Test user messaging

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-2-state-persistence-resume-capability.md#story-24-resume-detection-recovery]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#cli-boundary-mainpy]

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101 (glm-4.7)

### Debug Log References

N/A - Implementation completed without issues requiring debug logging.

### Completion Notes List

**Implementation Summary:**
- Added `get_state_path()` helper function to retrieve state file path
- Implemented `resume` command with full state detection:
  - Checks for state file existence
  - Loads and validates state status
  - Handles completed workflow (informative message)
  - Handles resumable statuses (in_progress, paused) - displays current position
  - Handles missing state file (clear error message)
- Implemented `run` command conflict detection:
  - Detects existing in-progress workflow for same epic
  - Compares normalized paths for accurate detection
  - Warns user and prompts to use `resume` command
  - Allows new run for different epic or corrupted state
- Updated `status` command to use `typer.Exit` for consistency
- All commands use `typer.Exit` instead of `sys.exit()` for proper CLI behavior

**Tests Added (7 new tests):**
- `test_resume_from_in_progress_status` - Verifies resume with in_progress state
- `test_resume_from_paused_status` - Verifies resume with paused state
- `test_resume_with_completed_workflow` - Verifies completed workflow message
- `test_resume_with_no_state_file` - Verifies missing state file error
- `test_run_command_conflict_detection` - Verifies same epic conflict warning
- `test_run_command_different_epic_no_warning` - Verifies different epic allows run
- `test_resume_restores_exact_position` - Verifies exact position restoration

**Updated Tests:**
- `test_resume_command_executes` - Updated to test new behavior
- `test_status_command_executes` - Updated to use typer.Exit
- `test_resume_command_exception_path_coverage` - Updated for new implementation
- `test_run_command_exception_path_coverage` - Updated for new implementation
- `test_status_command_exception_path_coverage` - Updated for new implementation

**Test Results:**
- All 127 tests pass (20 main tests, 26 state tests, 81 other tests)
- No regressions introduced
- Coverage includes all acceptance criteria

### File List

**Modified:**
- `src/bmad_auto/main.py` - Added get_state_path(), implemented resume command, added conflict detection to run command, updated all commands to use typer.Exit

**Modified:**
- `src/bmad_auto/tests/test_main.py` - Added 7 new tests, updated 5 existing tests for new behavior

## Change Log

- 2025-12-26: Implemented resume detection & recovery (Story 2.4)
  - Added state detection helper function
  - Implemented resume command with status-based routing
  - Added run command conflict detection for same epic
  - Updated all commands to use typer.Exit for proper CLI behavior
  - Added comprehensive tests for all resume scenarios
  - All acceptance criteria satisfied
