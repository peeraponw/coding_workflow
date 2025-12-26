# Story 1.1: Shared Module Setup

Status: ready-for-dev

## Story

As a **developer**,
I want **a shared module with constants, types, and exceptions**,
so that **all other modules have consistent definitions to import from**.

## Acceptance Criteria

1. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `consts.py` with EXIT_SUCCESS (0), EXIT_ERROR (1), EXIT_PAUSED (2), EXIT_CONFIG_ERROR (3)
2. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `consts.py` with AGENT_SM, AGENT_DEV, AGENT_REVIEWER
3. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `consts.py` with PHASE_SM, PHASE_DEV, PHASE_REVIEW
4. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `consts.py` with STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_PAUSED, STATUS_COMPLETED, STATUS_FAILED
5. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `types.py` with type aliases for common patterns
6. **Given** the project is initialized, **When** I import from `bmad_auto.shared`, **Then** I can access `exceptions.py` with BmadAutoError, ConfigError, StateCorruptionError, AgentError, WorkflowPausedError
7. All modules pass pyright type checking
8. ruff linting passes with no errors

## Tasks / Subtasks

- [ ] Task 1: Create shared module directory structure (AC: 1-6)
  - [ ] Create `src/bmad_auto/shared/__init__.py`
  - [ ] Export all public constants, types, and exceptions
- [ ] Task 2: Implement `consts.py` (AC: 1-4)
  - [ ] Define EXIT_SUCCESS, EXIT_ERROR, EXIT_PAUSED, EXIT_CONFIG_ERROR
  - [ ] Define AGENT_SM, AGENT_DEV, AGENT_REVIEWER
  - [ ] Define PHASE_SM, PHASE_DEV, PHASE_REVIEW
  - [ ] Define STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_PAUSED, STATUS_COMPLETED, STATUS_FAILED
- [ ] Task 3: Implement `types.py` (AC: 5)
  - [ ] Define type aliases for common patterns (e.g., StoryId, EpicPath, etc.)
  - [ ] Use TypeAlias from typing module
- [ ] Task 4: Implement `exceptions.py` (AC: 6)
  - [ ] Define BmadAutoError base exception
  - [ ] Define ConfigError, StateCorruptionError, AgentError, WorkflowPausedError
- [ ] Task 5: Verify type checking and linting (AC: 7-8)
  - [ ] Run pyright on all modules
  - [ ] Run ruff and fix any issues
- [ ] Task 6: Write unit tests
  - [ ] Test that all constants are accessible
  - [ ] Test that exceptions can be raised and caught
  - [ ] Test type annotations

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** All constants MUST live in `shared/consts.py` - no magic numbers/strings elsewhere
- Constants use UPPER_SNAKE_CASE naming convention
- Exception hierarchy follows domain-driven design: base class `BmadAutoError` with specific subclasses
- Use absolute imports: `from bmad_auto.shared.consts import EXIT_SUCCESS`
- File limit: ≤500 lines per file

### Source Tree Components

```
src/bmad_auto/
├── __init__.py
└── shared/
    ├── __init__.py      # Re-export public API
    ├── consts.py        # All constants
    ├── types.py         # Type aliases
    └── exceptions.py    # Domain exceptions
```

### Testing Standards

- Tests co-located in `src/bmad_auto/shared/tests/`
- Use pytest only (no unittest)
- 80% minimum coverage target
- Create `conftest.py` for shared fixtures

### Project Structure Notes

- This is the foundational module - all other modules will depend on it
- No external dependencies beyond Python stdlib for this module
- Must be importable without side effects

### References

- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#constants-per-agentsmd-24]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#complete-project-directory-structure]
- [Source: _bmad-output/project-context.md#cli-exit-codes]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
