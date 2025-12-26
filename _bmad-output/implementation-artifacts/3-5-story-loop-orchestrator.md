# Story 3.5: Story Loop Orchestrator

Status: done

## Story

As a **user**,
I want **the full SM → Dev → Review loop to run automatically**,
so that **stories are implemented and validated without manual intervention**.

## Acceptance Criteria

1. **Given** an epic with stories is parsed, **When** I run `bmad-auto run --epic path/to/epic.md`, **Then** for each story:
   - SM agent creates/refines the story (FR5)
   - Dev agent implements the story (FR6)
   - Reviewer agent validates the implementation (FR7)
   - If review fails, loop back to Dev with feedback (FR8)
   - If review passes, mark story complete
2. **Given** a review iteration, **When** the Reviewer rejects the implementation, **Then** Dev receives the feedback and implements fixes, and the loop continues until approval or max iterations
3. **Given** max review iterations (3) is reached, **When** the Reviewer still rejects, **Then** workflow pauses with `status: paused` and `error.type: review_failed`, and user can intervene and resume
4. State is saved after each phase transition (FR12)
5. Tests verify the complete loop with mocked agents

## Tasks / Subtasks

- [x] Task 1: Create orchestrator module (AC: 1)
  - [x] Create `src/bmad_auto/core/orchestrator.py`
  - [x] Implement WorkflowOrchestrator class
  - [x] Accept state and agent factory in constructor
- [x] Task 2: Implement story loop (AC: 1)
  - [x] Iterate through stories from parsed epic
  - [x] For each story, execute SM → Dev → Review sequence
  - [x] Track current story in state
- [x] Task 3: Implement phase execution (AC: 1)
  - [x] Implement `run_sm_phase()` - create story
  - [x] Implement `run_dev_phase()` - implement story
  - [x] Implement `run_review_phase()` - validate implementation
- [x] Task 4: Implement review iteration loop (AC: 2)
  - [x] Track iteration count in state
  - [x] Pass feedback to Dev on rejection
  - [x] Loop until approval
- [x] Task 5: Implement max iteration handling (AC: 3)
  - [x] Define MAX_REVIEW_ITERATIONS = 3
  - [x] Pause workflow on max iterations reached
  - [x] Set error.type = "review_failed"
- [x] Task 6: Implement state saving (AC: 4)
  - [x] Save state after SM phase
  - [x] Save state after Dev phase
  - [x] Save state after Review phase
- [x] Task 7: Write tests (AC: 5)
  - [x] Test complete loop with mocked agents
  - [x] Test review iteration
  - [x] Test max iteration pause

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Orchestrator OWNS workflow state transitions
- Orchestrator DELEGATES to agents/ for execution, state.py for I/O, git/ for commits
- Save state after EVERY phase transition
- Never put file I/O or git commands directly in orchestrator

### Orchestrator Flow

```
┌─────────────────────────────────────────────────────────┐
│                  bmad-auto Orchestrator                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │           WorkflowState (in-memory + YAML)         │  │
│  │  epic_content, current_story, git_diff, feedback   │  │
│  └───────────────────────────────────────────────────┘  │
│         │                    │                    │      │
│         ▼                    ▼                    ▼      │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐│
│   │  Claude  │         │  Claude  │         │  Claude  ││
│   │   (SM)   │         │  (Dev)   │         │(Reviewer)││
│   └──────────┘         └──────────┘         └──────────┘│
└─────────────────────────────────────────────────────────┘
```

### Story Loop Pattern

```python
async def run_epic(self, epic_path: str):
    epic = parse_epic(epic_path)
    for i, story in enumerate(epic.stories):
        self.state.current_story.id = story.id
        await self.run_story(story)
        self.state.stories.current_index = i + 1
        save(self.state)

async def run_story(self, story: Story):
    # SM phase
    self.state.current_story.phase = PHASE_SM
    await self.run_sm_phase(story)
    save(self.state)

    # Dev → Review loop
    for iteration in range(MAX_REVIEW_ITERATIONS):
        self.state.current_story.phase = PHASE_DEV
        self.state.current_story.iteration = iteration + 1
        await self.run_dev_phase(story)
        save(self.state)

        self.state.current_story.phase = PHASE_REVIEW
        result = await self.run_review_phase(story)
        save(self.state)

        if result.approved:
            break
    else:
        # Max iterations reached
        self.pause_with_error("review_failed")
```

### Source Tree Components

```
src/bmad_auto/core/
├── orchestrator.py   # WorkflowOrchestrator
└── tests/
    └── test_orchestrator.py
```

### Testing Standards

- Mock all agents for unit tests
- Test each phase transition
- Test state saving at each point

### References

- [Source: _bmad-output/architecture/core-architectural-decisions.md#agent-orchestration]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#orchestrator-boundary-coreorchestratorpy]
- [Source: _bmad-output/project-context.md#orchestrator-boundaries]

## Dev Agent Record

### Agent Model Used
glm-4.7 (via Claude Code)

### Debug Log References
None - implementation was straightforward

### Completion Notes List
- All 5 AC verified
- 12 tests written and passing
- pyright 0 errors
- Orchestrator owns state transitions per architecture
- Delegates to agents/, state.py as designed
- Saves state after every phase transition
- Review approval detection uses keyword heuristics

### File List
- src/bmad_auto/core/orchestrator.py
- src/bmad_auto/core/tests/test_orchestrator.py
