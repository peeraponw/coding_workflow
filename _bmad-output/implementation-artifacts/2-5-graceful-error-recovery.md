# Story 2.5: Graceful Error Recovery

Status: ready-for-dev

## Story

As a **user**,
I want **the workflow to pause gracefully on errors**,
so that **I can retry after fixing the issue without losing work**.

## Acceptance Criteria

1. **Given** a workflow is executing, **When** a rate limit error (429) occurs, **Then** state is saved with `status: paused` and `error.type: rate_limit` (FR15), workflow exits with code 2 (EXIT_PAUSED), and log message: "Rate limit exceeded. Run 'bmad-auto resume' to continue."
2. **Given** a workflow is executing, **When** an API error occurs (500, timeout, network), **Then** state is saved with `status: paused` and `error.type: api_error` (FR16), workflow exits with code 2 (EXIT_PAUSED), and log message includes error details and resume instruction
3. **Given** an unexpected error occurs, **When** the error handler catches it, **Then** state integrity is preserved (FR34), previously completed stories remain committed (NFR5), and current phase progress is saved
4. Tests verify graceful pause for each error type
5. Tests verify state integrity after errors

## Tasks / Subtasks

- [ ] Task 1: Define error types in state (AC: 1-3)
  - [ ] Add error type constants: rate_limit, api_error, unexpected
  - [ ] Ensure error section in state captures type, message, phase
- [ ] Task 2: Implement rate limit handling (AC: 1)
  - [ ] Detect 429 response from Claude SDK
  - [ ] Save state with paused status and rate_limit error
  - [ ] Log user-friendly message with resume instruction
  - [ ] Exit with EXIT_PAUSED (2)
- [ ] Task 3: Implement API error handling (AC: 2)
  - [ ] Detect 500, timeout, network errors
  - [ ] Save state with paused status and api_error type
  - [ ] Include error details in log message
  - [ ] Exit with EXIT_PAUSED (2)
- [ ] Task 4: Implement catch-all error handler (AC: 3)
  - [ ] Wrap orchestrator main loop in try/except
  - [ ] Always save state before exiting
  - [ ] Preserve completed story commits
  - [ ] Log unexpected error with stack trace
- [ ] Task 5: Write tests (AC: 4-5)
  - [ ] Test rate limit triggers pause
  - [ ] Test API error triggers pause
  - [ ] Test state integrity after error
  - [ ] Test exit codes

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Always save state before exiting on error
- Use WorkflowPausedError for recoverable errors
- Completed commits are never rolled back
- Error details stored in state for debugging

### Error Type Constants

```python
# In shared/consts.py
ERROR_RATE_LIMIT = "rate_limit"
ERROR_API = "api_error"
ERROR_UNEXPECTED = "unexpected"
```

### Error Handling Pattern

```python
async def run_workflow(state: WorkflowState):
    try:
        # Main workflow loop
        await execute_story_loop(state)
    except RateLimitError as e:
        state.workflow.status = STATUS_PAUSED
        state.error.type = ERROR_RATE_LIMIT
        state.error.message = str(e)
        state.error.phase = state.current_story.phase
        save(state)
        console.print("[yellow]Rate limit exceeded. Run 'bmad-auto resume' to continue.[/yellow]")
        raise typer.Exit(EXIT_PAUSED)
    except APIError as e:
        state.workflow.status = STATUS_PAUSED
        state.error.type = ERROR_API
        # ... similar handling
    except Exception as e:
        state.workflow.status = STATUS_PAUSED
        state.error.type = ERROR_UNEXPECTED
        # ... log full stack trace
```

### Source Tree Components

```
src/bmad_auto/core/
├── orchestrator.py   # Error handling in workflow loop
└── tests/
    └── test_orchestrator.py
```

### Testing Standards

- Mock Claude SDK to raise specific errors
- Verify state file contains correct error info
- Verify exit codes match expected

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-2-state-persistence-resume-capability.md#story-25-graceful-error-recovery]
- [Source: _bmad-output/project-context.md#cli-exit-codes]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
