# Story 3.6: Context Passing via YAML Handoff

Status: done

## Story

As a **developer**,
I want **context passed between agents via YAML handoff files**,
so that **each agent has the information it needs without prompt pollution**.

## Acceptance Criteria

1. **Given** SM agent completes, **When** handoff to Dev occurs, **Then** a YAML file is created with: story content from SM, acceptance criteria, any relevant context
2. **Given** Dev agent completes, **When** handoff to Reviewer occurs, **Then** a YAML file is created with: original story content, implementation summary, files changed, git diff reference
3. **Given** Reviewer provides feedback, **When** handoff back to Dev occurs, **Then** a YAML file is created with: review feedback, specific issues to address, previous iteration context
4. Handoff files are stored in `.bmad-auto/handoffs/` directory (FR11)
5. Handoff files are human-readable for debugging
6. Tests verify handoff file creation and content

## Tasks / Subtasks

- [x] Task 1: Create handoff module (AC: 1-4)
  - [x] Create handoff file management utilities
  - [x] Define handoff directory: `.bmad-auto/handoffs/`
  - [x] Implement file creation with proper naming
- [x] Task 2: Implement SM → Dev handoff (AC: 1)
  - [x] Create `sm_to_dev_handoff.yaml`
  - [x] Include story content and acceptance criteria
  - [x] Include any context from SM agent output
- [x] Task 3: Implement Dev → Reviewer handoff (AC: 2)
  - [x] Create `dev_to_reviewer_handoff.yaml`
  - [x] Include original story content
  - [x] Include implementation summary
  - [x] Include files changed list
  - [x] Include git diff reference
- [x] Task 4: Implement Reviewer → Dev handoff (AC: 3)
  - [x] Create `reviewer_to_dev_handoff.yaml`
  - [x] Include review feedback
  - [x] Include specific issues list
  - [x] Include previous iteration context
- [x] Task 5: Ensure human-readability (AC: 5)
  - [x] Use clear YAML formatting
  - [x] Add comments for context
  - [x] Use readable key names
- [x] Task 6: Write tests (AC: 6)
  - [x] Test handoff file creation
  - [x] Test file content structure
  - [x] Test directory creation

## Dev Notes

### Architecture Patterns & Constraints

- Handoff files are intermediate artifacts, not state
- Files should be human-readable for debugging
- Clean up old handoff files after successful story completion
- Use pyyaml for file creation

### Handoff Directory Structure

```
.bmad-auto/
└── handoffs/
    ├── story-1-1/
    │   ├── sm_to_dev.yaml
    │   ├── dev_to_reviewer.yaml
    │   └── reviewer_to_dev_iter1.yaml
    └── story-1-2/
        └── ...
```

### Handoff File Formats

**SM → Dev:**
```yaml
# Handoff: SM → Dev
# Story: 1-1-user-authentication
# Generated: 2025-12-26T14:23:07Z

story:
  id: "1-1"
  title: "User Authentication"
  content: |
    As a user, I want to authenticate...

acceptance_criteria:
  - "Given valid credentials, when I log in, then I see dashboard"
  - "Given invalid credentials, when I log in, then I see error"

context:
  notes: "Consider using JWT tokens"
  constraints: "Must integrate with existing user model"
```

**Dev → Reviewer:**
```yaml
# Handoff: Dev → Reviewer
story:
  id: "1-1"
  title: "User Authentication"

implementation:
  summary: "Added login endpoint with JWT authentication"
  files_changed:
    - src/bmad_auto/features/auth/handler.py
    - src/bmad_auto/features/auth/models.py
  diff_reference: ".bmad-auto/diffs/story-1-1.diff"
```

**Reviewer → Dev:**
```yaml
# Handoff: Reviewer → Dev (Iteration 2)
feedback:
  approved: false
  issues:
    - "Missing input validation on email field"
    - "JWT expiry not configurable"
  suggestions:
    - "Add pydantic validation for LoginRequest"

previous_context:
  iteration: 1
  files_touched:
    - src/bmad_auto/features/auth/handler.py
```

### Source Tree Components

```
src/bmad_auto/core/
├── orchestrator.py   # Calls handoff utilities
├── handoff.py        # Handoff file management
└── tests/
    └── test_handoff.py
```

### Testing Standards

- Use tmp_path for test handoff directory
- Verify YAML structure
- Test file cleanup

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-3-agent-orchestration-story-loop.md#story-36-context-passing-via-yaml-handoff]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#agent-orchestration]

## Dev Agent Record

### Agent Model Used
glm-4.7 (via Claude Code)

### Debug Log References
None - implementation was straightforward

### Completion Notes List
- All 6 AC verified
- 14 tests written and passing
- pyright 0 errors
- Handoff files are human-readable YAML with comments
- Stored in `.bmad-auto/handoffs/{story_id}/`
- Cleanup function removes handoffs after story completion

### File List
- src/bmad_auto/core/handoff.py
- src/bmad_auto/core/tests/test_handoff.py
