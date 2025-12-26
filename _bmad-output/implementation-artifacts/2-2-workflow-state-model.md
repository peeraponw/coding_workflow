# Story 2.2: Workflow State Model

Status: done

## Story

As a **developer**,
I want **a comprehensive WorkflowState dataclass**,
so that **all workflow progress can be tracked and persisted**.

## Acceptance Criteria

1. **Given** the state module is implemented, **When** I create a WorkflowState instance, **Then** it includes all required fields:
   - `workflow.epic_path`: path to the epic file
   - `workflow.status`: pending | in_progress | paused | completed | failed
   - `workflow.branch`: git branch name
   - `stories.total`: total story count
   - `stories.current_index`: 0-based index of current story
   - `stories.completed`: list of {story_id, commit_hash}
   - `current_story.id`: current story identifier
   - `current_story.phase`: sm | dev | review
   - `current_story.iteration`: review iteration count
   - `current_story.started_at`: ISO timestamp
   - `error.type`: error classification (if any)
   - `error.message`: error details (if any)
   - `error.phase`: phase where error occurred
2. State model matches the YAML format from Architecture doc
3. All fields have appropriate type hints
4. Tests verify state model creation and validation

## Tasks / Subtasks

- [x] Task 1: Create state module with dataclasses (AC: 1)
  - [x] Create `src/bmad_auto/core/state.py`
  - [x] Define WorkflowSection dataclass (epic_path, status, branch)
  - [x] Define StoriesSection dataclass (total, current_index, completed)
  - [x] Define CurrentStorySection dataclass (id, phase, iteration, started_at)
  - [x] Define ErrorSection dataclass (type, message, phase)
  - [x] Define main WorkflowState dataclass composing all sections
- [x] Task 2: Define status enum/constants (AC: 1)
  - [x] Use STATUS_* constants from shared/consts.py
  - [x] Use PHASE_* constants from shared/consts.py
- [x] Task 3: Add type hints (AC: 3)
  - [x] Use Optional for nullable fields
  - [x] Use list[CompletedStory] for completed stories
  - [x] Use proper datetime types for timestamps
- [x] Task 4: Add factory methods (AC: 1)
  - [x] `WorkflowState.new(epic_path, story_count)` - create initial state
  - [x] `WorkflowState.from_dict(data)` - create from YAML dict
  - [x] `to_dict()` - serialize to YAML-compatible dict
- [x] Task 5: Write tests (AC: 4)
  - [x] Test state creation with all fields
  - [x] Test serialization round-trip
  - [x] Test default values

## Dev Notes

### Architecture Patterns & Constraints

- Dataclasses for clean, typed state representation
- Match exact YAML structure from architecture doc
- Use constants from shared/consts.py for status/phase values
- State must be serializable to YAML

### YAML State Format

```yaml
workflow:
  epic_path: "docs/epics/epic-001.md"
  status: "in_progress"
  branch: "epic/epic-001"

stories:
  total: 5
  current_index: 2
  completed:
    - story_id: "story-1"
      commit: "abc123"
    - story_id: "story-2"
      commit: "def456"

current_story:
  id: "story-3"
  phase: "dev"
  iteration: 1
  started_at: "2025-12-26T14:23:07Z"

error:
  type: null
  message: null
  phase: null
```

### Source Tree Components

```
src/bmad_auto/core/
├── state.py        # WorkflowState dataclasses
└── tests/
    └── test_state.py
```

### Testing Standards

- Test dataclass instantiation
- Test to_dict/from_dict round-trip
- Test default values and optional fields

### References

- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#state-file-format]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#state-boundary-corestatespy]

## Dev Agent Record

### Agent Model Used

claude-opus-4-5-20251101

### Debug Log References

None - implementation completed without issues.

### Completion Notes List

- Implemented 5 frozen dataclasses: CompletedStory, WorkflowSection, StoriesSection, CurrentStorySection, ErrorSection
- WorkflowState composes all sections with frozen immutability
- Factory method `WorkflowState.new()` creates initial state with proper defaults
- `to_dict()`/`from_dict()` enable YAML serialization with datetime ISO format
- Uses existing STATUS_* and PHASE_* constants from shared/consts.py
- All 11 tests pass (dataclass creation, serialization, round-trip, defaults)
- Full test suite (105 tests) passes with no regressions

### File List

- `src/bmad_auto/core/state.py` (new) - WorkflowState dataclasses with factory methods and serialization
- `src/bmad_auto/core/tests/test_state.py` (new) - Comprehensive tests for state model
