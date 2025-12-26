# Story 2.2: Workflow State Model

Status: ready-for-dev

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

- [ ] Task 1: Create state module with dataclasses (AC: 1)
  - [ ] Create `src/bmad_auto/core/state.py`
  - [ ] Define WorkflowSection dataclass (epic_path, status, branch)
  - [ ] Define StoriesSection dataclass (total, current_index, completed)
  - [ ] Define CurrentStorySection dataclass (id, phase, iteration, started_at)
  - [ ] Define ErrorSection dataclass (type, message, phase)
  - [ ] Define main WorkflowState dataclass composing all sections
- [ ] Task 2: Define status enum/constants (AC: 1)
  - [ ] Use STATUS_* constants from shared/consts.py
  - [ ] Use PHASE_* constants from shared/consts.py
- [ ] Task 3: Add type hints (AC: 3)
  - [ ] Use Optional for nullable fields
  - [ ] Use list[CompletedStory] for completed stories
  - [ ] Use proper datetime types for timestamps
- [ ] Task 4: Add factory methods (AC: 1)
  - [ ] `WorkflowState.new(epic_path, story_count)` - create initial state
  - [ ] `WorkflowState.from_dict(data)` - create from YAML dict
  - [ ] `to_dict()` - serialize to YAML-compatible dict
- [ ] Task 5: Write tests (AC: 4)
  - [ ] Test state creation with all fields
  - [ ] Test serialization round-trip
  - [ ] Test default values

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

### Debug Log References

### Completion Notes List

### File List
