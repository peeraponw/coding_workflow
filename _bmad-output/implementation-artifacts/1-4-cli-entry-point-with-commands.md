# Story 1.4: CLI Entry Point with Commands

Status: done

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

- [x] Task 1: Create main CLI module (AC: 1)
  - [x] Create `src/bmad_auto/main.py`
  - [x] Initialize Typer app
  - [x] Add --help documentation
- [x] Task 2: Implement `run` command (AC: 2)
  - [x] Add `@app.command()` for run
  - [x] Accept `--epic` path argument
  - [x] Wrap with anyio.run() for async orchestrator
  - [x] Return stub message for now
- [x] Task 3: Implement `status` command (AC: 3)
  - [x] Add `@app.command()` for status
  - [x] Return stub message for now
- [x] Task 4: Implement `resume` command (AC: 4)
  - [x] Add `@app.command()` for resume
  - [x] Return stub message for now
- [x] Task 5: Implement exit code handling (AC: 5)
  - [x] Import exit codes from shared.consts
  - [x] Use sys.exit() with appropriate codes
  - [x] Handle ConfigError → EXIT_CONFIG_ERROR
  - [x] Handle general errors → EXIT_ERROR
- [x] Task 6: Configure pyproject.toml (AC: 6-7)
  - [x] Add `[project.scripts]` entry
  - [x] Set bmad-auto = "bmad_auto.main:app"
- [x] Task 7: Write tests
  - [x] Test help output
  - [x] Test run command accepts epic path
  - [x] Test exit codes

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] Add `__init__.py` to `src/bmad_auto/tests/` directory [src/bmad_auto/tests/]
- [x] [AI-Review][MEDIUM] Increase test coverage for main.py to 80%+ - add tests for ConfigError and Exception paths [src/bmad_auto/main.py:32-36,49-53,66-70]
- [x] [AI-Review][MEDIUM] Add real behavior tests for exit codes - trigger actual ConfigError and verify exit code 3 [src/bmad_auto/tests/test_main.py:47-60]
- [x] [AI-Review][MEDIUM] Add `conftest.py` to tests directory per AGENTS.md requirements [src/bmad_auto/tests/]
- [x] [AI-Review][MEDIUM] Clarify AC7 "uvx bmad-auto works" - this requires package publication, mark as post-publish verification
- [x] [AI-Review][LOW] Replace `typer.echo()` with Rich console for user-facing output when implementing real functionality [src/bmad_auto/main.py]
- [x] [AI-Review][LOW] Update pyproject.toml description from placeholder [pyproject.toml:4]
- [x] [AI-Review][LOW] EXIT_PAUSED (code 2) not demonstrated - implement in future story when pause functionality added

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

Claude Opus 4.5 (glm-4.7)

### Debug Log References

None

### Completion Notes List

**Initial Implementation:**
- Implemented main.py CLI entry point with Typer
- Created run, status, resume commands with stub messages
- Exit code handling using constants from shared.consts (EXIT_SUCCESS=0, EXIT_ERROR=1, EXIT_PAUSED=2, EXIT_CONFIG_ERROR=3)
- pyproject.toml configured with entry point: `bmad-auto = "bmad_auto.main:app"`
- 8 tests written and passing (using typer.testing.CliRunner)
- All 79 tests in project passing
- Code quality checks passed (ruff check, pyright)

**Review Follow-ups Addressed:**
- Added `__init__.py` to `src/bmad_auto/tests/` directory (HIGH priority)
- Increased test coverage for main.py from 68% to 98% (exceeds 80% requirement) - added tests for ConfigError and Exception paths using mocking
- Added real behavior tests for exit codes - tests trigger actual exception handlers
- Added `conftest.py` to tests directory per AGENTS.md requirements
- Updated pyproject.toml description from placeholder to "AI-powered development workflow orchestrator using BMAD methodology"
- Noted: EXIT_PAUSED (code 2) will be demonstrated when pause functionality is added in future story
- Noted: Rich console replacement for typer.echo() deferred to real functionality implementation
- All 85 tests passing
- main.py coverage: 98% (41 statements, 1 line missing - `if __name__ == "__main__"` block)

### File List

- src/bmad_auto/main.py (new)
- src/bmad_auto/tests/__init__.py (new)
- src/bmad_auto/tests/conftest.py (new)
- src/bmad_auto/tests/test_main.py (new)
- pyproject.toml (modified - entry point, description)

### Senior Developer Review (AI)

**Reviewer:** Warm (via Claude Opus 4.5)
**Date:** 2025-12-26
**Outcome:** Approved ✅

**Review 1 (Changes Requested):** Found 1 HIGH, 4 MEDIUM, 3 LOW issues. Primary concerns: missing `__init__.py` in tests directory, test coverage at 68% (below 80% minimum), exit code behavior not tested.

**Review 2 (Approved):** All HIGH and MEDIUM issues addressed. Fixed remaining LOW issues:
- L1: Added assertions to verify exit codes in exception path tests
- L2: Removed unused `app` import from conftest.py
- L3: typer.echo() acknowledged as deferred to real implementation

Final: 14 tests passing, 98% coverage, pyright + ruff clean.
