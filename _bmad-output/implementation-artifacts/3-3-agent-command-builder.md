# Story 3.3: Agent Command Builder

Status: ready-for-dev

## Story

As a **developer**,
I want **command builders for SM, Dev, and Reviewer agents**,
so that **the orchestrator can construct correct skill commands**.

## Acceptance Criteria

1. **Given** I need to invoke the SM agent, **When** I call `build_sm_command(epic_content, story_index)`, **Then** I get a command string like: `/bmad:bmm:agents:sm create story {story_index} from epic`
2. **Given** I need to invoke the Dev agent, **When** I call `build_dev_command(story_content)`, **Then** I get a command string like: `/bmad:bmm:agents:dev implement story`
3. **Given** I need to invoke the Reviewer agent, **When** I call `build_reviewer_command(story_content, implementation_diff)`, **Then** I get a command string like: `/bmad:bmm:workflows:code-review review implementation`
4. Commands include necessary context references
5. Tests verify command format for each agent role

## Tasks / Subtasks

- [ ] Task 1: Create prompts module (AC: 1-4)
  - [ ] Create `src/bmad_auto/agents/prompts.py`
  - [ ] Define command builder functions
- [ ] Task 2: Implement build_sm_command (AC: 1)
  - [ ] Accept epic_content and story_index parameters
  - [ ] Build skill command with story number
  - [ ] Include context as needed
- [ ] Task 3: Implement build_dev_command (AC: 2)
  - [ ] Accept story_content parameter
  - [ ] Build skill command for implementation
  - [ ] Reference story file or content
- [ ] Task 4: Implement build_reviewer_command (AC: 3)
  - [ ] Accept story_content and implementation_diff
  - [ ] Build code-review workflow command
  - [ ] Include review context
- [ ] Task 5: Write tests (AC: 5)
  - [ ] Test SM command format
  - [ ] Test Dev command format
  - [ ] Test Reviewer command format
  - [ ] Test context inclusion

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Use bmad skill commands, never raw prompts
- Command builders are pure functions
- Context passed via command parameters, not prompt pollution
- Skill command format: `/bmad:bmm:agents:{agent} {action}`

### Command Patterns

```python
def build_sm_command(epic_content: str, story_index: int) -> str:
    """Build SM agent command for story creation."""
    return f"/bmad:bmm:agents:sm create story {story_index} from epic"

def build_dev_command(story_file: str) -> str:
    """Build Dev agent command for story implementation."""
    return f"/bmad:bmm:workflows:dev-story implement {story_file}"

def build_reviewer_command(story_file: str) -> str:
    """Build Reviewer agent command for code review."""
    return f"/bmad:bmm:workflows:code-review review {story_file}"
```

### Context Passing Strategy

- SM: Epic content loaded by agent from file reference
- Dev: Story file path passed in command
- Reviewer: Story file + implementation references

### Source Tree Components

```
src/bmad_auto/agents/
├── __init__.py
├── base.py
├── claude.py
├── prompts.py       # Command builder functions
└── tests/
    └── test_prompts.py
```

### Testing Standards

- Test command string format
- Test with various input parameters
- Verify no prompt pollution

### References

- [Source: _bmad-output/project-context.md#agent-invocation-pattern]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#file-purpose-summary]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
