# Story 3.2: Claude Agent Adapter

Status: ready-for-dev

## Story

As a **developer**,
I want **a Claude Agent SDK wrapper implementing AgentProtocol**,
so that **I can invoke Claude-based agents uniformly**.

## Acceptance Criteria

1. **Given** Claude Agent SDK is available, **When** I create a ClaudeAgent instance, **Then** it implements AgentProtocol
2. **Given** a ClaudeAgent instance, **When** I call `await agent.run("/bmad:bmm:agents:sm create story")`, **Then** the command is executed via Claude Agent SDK (FR5, FR6, FR7) and AgentResult is returned with output or error
3. **Given** the agent execution fails, **When** an API error occurs, **Then** AgentResult.success is False and AgentResult.error contains the error message
4. Adapter uses anyio for async compatibility (NFR6)
5. Tests use mocked SDK responses
6. Integration tests verify real agent invocation

## Tasks / Subtasks

- [ ] Task 1: Create ClaudeAgent class (AC: 1)
  - [ ] Create `src/bmad_auto/agents/claude.py`
  - [ ] Implement AgentProtocol interface
  - [ ] Accept configuration in constructor
- [ ] Task 2: Implement run method (AC: 2)
  - [ ] Import Claude Agent SDK
  - [ ] Execute command via SDK
  - [ ] Capture output from agent response
  - [ ] Return AgentResult with success and output
- [ ] Task 3: Implement error handling (AC: 3)
  - [ ] Catch SDK exceptions
  - [ ] Map to AgentResult.fail()
  - [ ] Include meaningful error messages
- [ ] Task 4: Ensure anyio compatibility (AC: 4)
  - [ ] Use anyio for async operations
  - [ ] Verify works with anyio.run()
- [ ] Task 5: Write unit tests with mocks (AC: 5)
  - [ ] Mock Claude Agent SDK
  - [ ] Test successful execution
  - [ ] Test error handling
- [ ] Task 6: Write integration test (AC: 6)
  - [ ] Mark with @pytest.mark.integration
  - [ ] Test real agent invocation

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Invoke bmad agents via skill commands, not raw prompts
- Use anyio for async (matches SDK internals)
- Never log credentials (NFR14)
- Adapter is stateless - state managed by orchestrator

### Agent Invocation Pattern

```python
# ✅ Correct: Use bmad skill commands
await agent.run("/bmad:bmm:agents:sm create stories from epics 02")
await agent.run("/bmad:bmm:agents:dev implement story-03")

# ❌ Wrong: Don't build prompts directly
await agent.run("You are an SM agent. Create stories...")
```

### Implementation

```python
from claude_agent_sdk import Agent  # Actual SDK import

class ClaudeAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    async def run(self, command: str) -> AgentResult:
        try:
            # Execute via Claude Agent SDK
            agent = Agent()
            result = await agent.run(command)
            return AgentResult.ok(result.output)
        except Exception as e:
            return AgentResult.fail(str(e))
```

### Source Tree Components

```
src/bmad_auto/agents/
├── __init__.py
├── base.py
├── claude.py        # ClaudeAgent implementation
└── tests/
    ├── conftest.py  # Mock agent fixtures
    └── test_claude.py
```

### Testing Standards

- Mock SDK at module level
- Test both success and failure paths
- Integration tests in tests/integration/

### References

- [Source: _bmad-output/project-context.md#agent-invocation-pattern]
- [Source: _bmad-output/architecture/core-architectural-decisions.md#async-execution-model]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#agent-boundary-agents]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
