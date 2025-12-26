# Story 1.4: CLI Entry Point with Commands

Status: ready-for-dev

## Story

As a **user**,
I want **to invoke bmad-auto commands from my terminal**,
so that **I can start workflows, check status, and resume paused work**.

## Acceptance Criteria

1. **Given** bmad-auto is installed via `uvx bmad-auto`, **When** I run `bmad-auto --help`, **Then** I see available commands: `run`, `status`, `resume`
2. **Given** the CLI is invoked, **When** I run `bmad-auto run --epic docs/epics/epic-001.md`, **Then** the command accepts the epic path argument (FR1, FR2) and returns a stub message (actual orchestration in Epic 3)
3. **Given** the CLI is invoked, **When** I run `bmad-auto status`, **Then** the command executes (stub for now, full implementation in Epic 4)
4. **Given** the CLI is invoked, **When** I run `bmad-auto resume`, **Then** the command executes (stub for now, full implementation in Epic 2)
5. **Given** any command fails, **When** an error occurs, **Then** the CLI exits with appropriate exit code: 0=success, 1=error, 2=paused, 3=config error (FR33)
6. pyproject.toml has `[project.scripts]` entry for `bmad-auto`
7. `uvx bmad-auto` works after installation

## Tasks / Subtasks

- [ ] Task 1: Create main CLI module (AC: 1)
  - [ ] Create `src/bmad_auto/main.py`
  - [ ] Initialize Typer app
  - [ ] Add --help documentation
- [ ] Task 2: Implement `run` command (AC: 2)
  - [ ] Add `@app.command()` for run
  - [ ] Accept `--epic` path argument
  - [ ] Wrap with anyio.run() for async orchestrator
  - [ ] Return stub message for now
- [ ] Task 3: Implement `status` command (AC: 3)
  - [ ] Add `@app.command()` for status
  - [ ] Return stub message for now
- [ ] Task 4: Implement `resume` command (AC: 4)
  - [ ] Add `@app.command()` for resume
  - [ ] Return stub message for now
- [ ] Task 5: Implement exit code handling (AC: 5)
  - [ ] Import exit codes from shared.consts
  - [ ] Use sys.exit() with appropriate codes
  - [ ] Handle ConfigError → EXIT_CONFIG_ERROR
  - [ ] Handle general errors → EXIT_ERROR
- [ ] Task 6: Configure pyproject.toml (AC: 6-7)
  - [ ] Add `[project.scripts]` entry
  - [ ] Set bmad-auto = "bmad_auto.main:app"
- [ ] Task 7: Write tests
  - [ ] Test help output
  - [ ] Test run command accepts epic path
  - [ ] Test exit codes

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Use Typer for CLI with anyio.run() at entry point
- Entry point wraps async orchestrator with anyio.run()
- Use exit codes from `shared/consts.py` - never bare integers
- Config is loaded before any command execution

### CLI Entry Pattern

```python
import anyio
import typer
from bmad_auto.shared.consts import EXIT_SUCCESS, EXIT_ERROR, EXIT_CONFIG_ERROR

app = typer.Typer()

@app.command()
def run(epic: str = typer.Option(..., "--epic", help="Path to epic file")):
    """Execute story loop for an epic."""
    try:
        anyio.run(orchestrator.run_epic, epic)
        raise typer.Exit(EXIT_SUCCESS)
    except ConfigError:
        raise typer.Exit(EXIT_CONFIG_ERROR)
```

### pyproject.toml Entry

```toml
[project.scripts]
bmad-auto = "bmad_auto.main:app"
```

### Source Tree Components

```
src/bmad_auto/
├── __init__.py       # Package version
└── main.py           # Typer CLI entry point
```

### Testing Standards

- Use typer.testing.CliRunner for CLI tests
- Test help output contains expected commands
- Test exit codes for error conditions

### References

- [Source: _bmad-output/architecture/core-architectural-decisions.md#async-execution-model]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#cli-boundary-mainpy]
- [Source: _bmad-output/project-context.md#cli-exit-codes]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
