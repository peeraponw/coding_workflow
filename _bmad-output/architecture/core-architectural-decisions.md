# Core Architectural Decisions

## Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Agent orchestration pattern
- Async execution model
- State persistence format (YAML - already decided)

**Important Decisions (Shape Architecture):**
- Logging strategy
- Testing strategy

**Deferred Decisions (Post-MVP):**
- TUI dashboard implementation
- Codex CLI integration pattern
- Multi-epic parallelism

## Agent Orchestration

**Decision:** Orchestrator-Managed State Pattern

**Description:** The orchestrator maintains all workflow state and injects relevant context into each agent's prompt. Agents do not communicate directly with each other.

**Rationale:**
- Clean separation of concerns
- State naturally persists to YAML for pause/resume
- No external dependencies (message buses, shared files)
- Orchestrator controls context scope to prevent pollution

**Implementation:**
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

**Affects:** All agent-related components, state manager, prompt builders

## Async Execution Model

**Decision:** anyio.run() at CLI entry point

**Description:** Typer commands are synchronous but immediately call `anyio.run()` to execute the async orchestrator.

**Rationale:**
- Matches Claude Agent SDK which uses anyio internally
- Keeps entire orchestration layer async
- Simple integration with Typer

**Implementation Pattern:**
```python
import anyio
import typer

app = typer.Typer()

@app.command()
def run(epic: str):
    """Execute story loop for an epic."""
    anyio.run(orchestrator.run_epic, epic)
```

**Affects:** CLI entry points, all orchestrator code

## Logging Strategy

**Decision:** Rich console output

**Description:** Use Rich (via typer[all]) for structured, pretty terminal output with timestamps and agent handoff visibility.

**Rationale:**
- Already included via typer[all] dependency
- Pretty, readable output for developer tool
- Sufficient for MVP; can add structlog later if needed

**Implementation:**
- Use `rich.console.Console` for output
- Timestamped log entries
- Color-coded agent phases (SM=blue, Dev=green, Reviewer=yellow)
- Progress indicators for long operations

**Affects:** All user-facing output, logging module

## Testing Strategy

**Decision:** Mock SDK + Integration Tests

**Description:**
- Unit tests: Mock Claude Agent SDK responses with pytest fixtures
- Integration tests: Real agent execution for critical paths

**Rationale:**
- Fast unit tests for development iteration
- Real integration tests ensure actual behavior works
- pytest-asyncio for async test support

**Implementation:**
```python
# Unit test with mock
@pytest.fixture
def mock_claude_agent():
    with patch('claude_agent_sdk.query') as mock:
        mock.return_value = AsyncIterator([...])
        yield mock

# Integration test marker
@pytest.mark.integration
async def test_full_story_loop():
    # Real agent execution
    ...
```

**Affects:** Test infrastructure, CI pipeline, development workflow

## Decision Impact Analysis

**Implementation Sequence:**
1. Project initialization (starter template)
2. CLI structure with Typer + anyio entry points
3. State manager (YAML persistence)
4. Agent adapters (Claude Agent SDK wrapper)
5. Orchestrator (state injection, agent coordination)
6. Git integration
7. Logging/output formatting

**Cross-Component Dependencies:**
- Orchestrator depends on: State manager, Agent adapters, Git handler
- Agent adapters depend on: Claude Agent SDK, Prompt builders
- CLI depends on: Orchestrator, Config loader
- All components depend on: Logging
