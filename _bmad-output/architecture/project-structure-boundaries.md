# Project Structure & Boundaries

## Requirements to Structure Mapping

| FR Category | Module Location |
|-------------|-----------------|
| Workflow Execution (FR1-4) | `core/orchestrator.py` |
| Agent Orchestration (FR5-11) | `agents/` |
| State Management (FR12-16) | `core/state.py` |
| Progress Monitoring (FR17-21) | `core/orchestrator.py` + `shared/logging.py` |
| Git Integration (FR22-25) | `features/git_integration/` |
| Configuration (FR26-31) | `core/config.py` |
| Error Handling (FR32-34) | `shared/exceptions.py` + all modules |

## Complete Project Directory Structure

```
bmad-auto/
├── README.md
├── pyproject.toml                    # hatchling build, entry points
├── uv.lock
├── .python-version
├── .gitignore
├── .env.example                      # ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL
│
├── src/
│   └── bmad_auto/
│       ├── __init__.py               # Package version
│       ├── main.py                   # Typer CLI entry point
│       │
│       ├── shared/
│       │   ├── __init__.py
│       │   ├── consts.py             # EXIT_*, AGENT_*, PHASE_*, STATUS_*
│       │   ├── types.py              # Type aliases, Protocols
│       │   ├── exceptions.py         # BmadAutoError hierarchy
│       │   └── logging.py            # structlog setup, Rich console
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py       # WorkflowOrchestrator (FR1-4, FR17-21)
│       │   ├── state.py              # WorkflowState, YAML persistence (FR12-16)
│       │   ├── config.py             # InternalSettings + UserConfig loader
│       │   └── tests/
│       │       ├── __init__.py
│       │       ├── conftest.py       # Shared fixtures
│       │       ├── test_orchestrator.py
│       │       ├── test_state.py
│       │       └── test_config.py
│       │
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py               # AgentProtocol, AgentResult
│       │   ├── claude.py             # ClaudeAgent (FR5-10)
│       │   ├── prompts.py            # PromptBuilder for SM/Dev/Reviewer
│       │   └── tests/
│       │       ├── __init__.py
│       │       ├── conftest.py       # Mock agent fixtures
│       │       ├── test_claude.py
│       │       └── test_prompts.py
│       │
│       └── features/
│           └── git_integration/
│               ├── __init__.py
│               ├── handler.py        # GitHandler (FR22-25)
│               └── tests/
│                   ├── __init__.py
│                   └── test_handler.py
│
└── tests/                            # Integration tests only
    ├── __init__.py
    ├── conftest.py                   # Integration test fixtures
    └── integration/
        ├── __init__.py
        └── test_full_workflow.py     # Real agent tests (@pytest.mark.integration)
```

## Architectural Boundaries

**CLI Boundary (`main.py`):**
- Entry point for all commands: `run`, `status`, `resume`
- Wraps async orchestrator with `anyio.run()`
- Returns exit codes from `shared/consts.py`

**Orchestrator Boundary (`core/orchestrator.py`):**
- Owns workflow state transitions
- Injects context into agent prompts
- Coordinates agent → state → git flow
- Never touches file I/O directly (delegates to state/git)

**Agent Boundary (`agents/`):**
- Abstract via `AgentProtocol`
- Agents receive prompts, return `AgentResult`
- No knowledge of workflow state or git

**State Boundary (`core/state.py`):**
- Owns YAML file I/O (atomic writes)
- Provides `WorkflowState` dataclass
- Validates state integrity on load

**Git Boundary (`features/git_integration/`):**
- Owns all git CLI subprocess calls
- Branch creation, commits, status checks
- No knowledge of agents or state

## Data Flow

```
User Command
     │
     ▼
┌─────────────┐
│   main.py   │  CLI parsing, anyio.run()
└─────┬───────┘
      │
      ▼
┌─────────────────┐
│  orchestrator   │  Workflow coordination
└─────┬───────────┘
      │
      ├──────────────────┬──────────────────┐
      ▼                  ▼                  ▼
┌───────────┐      ┌───────────┐      ┌───────────┐
│  agents/  │      │  state.py │      │   git/    │
│  claude   │      │   YAML    │      │  handler  │
└───────────┘      └───────────┘      └───────────┘
      │                  │                  │
      ▼                  ▼                  ▼
Claude Agent SDK   .bmad-auto-state.yaml   git CLI
```

## File Purpose Summary

| File | Purpose | FR Coverage |
|------|---------|-------------|
| `main.py` | CLI entry, Typer commands | FR1-2 |
| `orchestrator.py` | Story loop, agent coordination | FR1-4, FR17-21 |
| `state.py` | YAML state read/write, atomic saves | FR12-16 |
| `config.py` | pydantic_settings + YAML user config | FR26-31 |
| `agents/base.py` | AgentProtocol, AgentResult | - |
| `agents/claude.py` | Claude Agent SDK wrapper | FR5-10 |
| `agents/prompts.py` | Prompt builders per role | FR11 |
| `git_integration/handler.py` | Branch/commit operations | FR22-25 |
| `shared/exceptions.py` | Domain exceptions | FR32-34 |
| `shared/consts.py` | All constants | FR33 |
| `shared/logging.py` | structlog + Rich setup | FR20-21 |
