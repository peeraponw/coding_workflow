# Story 2.3: State Persistence with Atomic Writes

Status: ready-for-dev

## Story

As a **user**,
I want **workflow state saved atomically after each phase**,
so that **unexpected termination never corrupts my progress**.

## Acceptance Criteria

1. **Given** a workflow is in progress, **When** a phase completes (SM done, Dev done, Review done), **Then** state is persisted to `.bmad-auto-state.yaml` (FR12)
2. **Given** state needs to be written, **When** the write operation executes, **Then** it uses atomic write (write to temp, then rename) (NFR1) and partial writes never leave corrupted state files
3. **Given** a state file exists, **When** state is loaded, **Then** the WorkflowState is reconstructed accurately and integrity is validated (NFR3)
4. **Given** a corrupted state file, **When** loading is attempted, **Then** StateCorruptionError is raised with clear message and user is informed how to recover
5. Tests verify atomic write behavior
6. Tests verify corruption detection

## Tasks / Subtasks

- [ ] Task 1: Implement state persistence in state.py (AC: 1)
  - [ ] Add `save(state: WorkflowState, path: Path)` function
  - [ ] Add `load(path: Path) -> WorkflowState` function
  - [ ] Use pyyaml for serialization
- [ ] Task 2: Implement atomic writes (AC: 2)
  - [ ] Write to temporary file first (`.tmp` suffix)
  - [ ] Use `os.rename()` or `Path.rename()` for atomic move
  - [ ] Ensure temp file cleanup on failure
- [ ] Task 3: Implement state loading with validation (AC: 3)
  - [ ] Load YAML file
  - [ ] Validate required fields exist
  - [ ] Convert to WorkflowState dataclass
  - [ ] Validate status values are legal
- [ ] Task 4: Implement corruption detection (AC: 4)
  - [ ] Detect malformed YAML
  - [ ] Detect missing required fields
  - [ ] Detect invalid status values
  - [ ] Raise StateCorruptionError with recovery hints
- [ ] Task 5: Write tests (AC: 5-6)
  - [ ] Test atomic write succeeds
  - [ ] Test atomic write cleans up temp file
  - [ ] Test load reconstructs state correctly
  - [ ] Test corruption detection for various cases

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Always use atomic writes (temp file + rename)
- State file path from user config: `.bmad-auto-state.yaml`
- Use pyyaml for YAML operations
- Raise StateCorruptionError from shared/exceptions.py

### Atomic Write Pattern

```python
def save(state: WorkflowState, path: Path) -> None:
    """Save state atomically."""
    temp_path = path.with_suffix('.tmp')
    try:
        temp_path.write_text(yaml.dump(state.to_dict()))
        temp_path.rename(path)  # Atomic on POSIX
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

### Corruption Recovery Message

```
StateCorruptionError: State file corrupted or invalid.

The file '.bmad-auto-state.yaml' appears to be corrupted.

To recover:
1. Check if backup exists: .bmad-auto-state.yaml.bak
2. Delete the corrupted file and restart with: bmad-auto run --epic <path>
3. Your completed stories (if any) remain committed in git
```

### Source Tree Components

```
src/bmad_auto/core/
├── state.py        # Add save/load functions
└── tests/
    └── test_state.py
```

### Testing Standards

- Use tmp_path fixture for test files
- Simulate corruption by writing invalid YAML
- Verify atomic behavior with process interruption

### References

- [Source: _bmad-output/project-context.md#state-persistence]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#state-boundary-corestatespy]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
