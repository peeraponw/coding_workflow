# Story 2.4: Resume Detection & Recovery

Status: ready-for-dev

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

- [ ] Task 1: Implement state detection in CLI (AC: 1-4)
  - [ ] Check for state file existence
  - [ ] Load state and check status
  - [ ] Route to appropriate handler based on status
- [ ] Task 2: Implement resume command (AC: 1)
  - [ ] Load existing state
  - [ ] Validate state has resumable status
  - [ ] Pass to orchestrator with resume context
  - [ ] Orchestrator continues from current_story.phase
- [ ] Task 3: Implement run command conflict detection (AC: 2)
  - [ ] Check if state file exists before starting new run
  - [ ] Compare epic paths
  - [ ] Warn user if in-progress workflow exists
  - [ ] Prompt to use resume instead
- [ ] Task 4: Handle edge cases (AC: 3-4)
  - [ ] Handle completed workflow resume attempt
  - [ ] Handle missing state file resume attempt
  - [ ] Provide clear user messages
- [ ] Task 5: Write comprehensive tests (AC: 5-6)
  - [ ] Test resume from in_progress
  - [ ] Test resume from paused
  - [ ] Test resume with completed workflow
  - [ ] Test resume with no state file
  - [ ] Test run conflict detection

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

### Debug Log References

### Completion Notes List

### File List
