---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments:
  - "_bmad-output/prd.md"
  - "_bmad-output/project-planning-artifacts/research/technical-claude-codex-cli-integration-research-2025-12-25.md"
workflowType: 'architecture'
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-26'
hasProjectContext: true
projectContextFile: "src/AGENTS.md"
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
34 requirements across 6 domains:
- **Workflow Execution (FR1-4):** Epic parsing, sequential story execution, single-command invocation
- **Agent Orchestration (FR5-11):** SM/Dev/Reviewer agent coordination, hierarchical model routing (Claude for SM/Reviewer, GLM for Dev), YAML handoff files
- **State Management (FR12-16):** YAML persistence, exact-point resume, graceful error recovery
- **Progress Monitoring (FR17-21):** Non-blocking status, timestamped logging, handoff event visibility
- **Git Integration (FR22-25):** Auto-branch creation, auto-commit with story references
- **Configuration & Error Handling (FR26-34):** YAML config, env var credentials, distinct exit codes

**Non-Functional Requirements:**
14 requirements across 3 domains:
- **Reliability (NFR1-5):** Atomic state writes, 100% resume reliability, corruption detection, atomic git ops
- **Integration (NFR6-11):** Claude Agent SDK, GLM via ANTHROPIC_BASE_URL, standard YAML parser, git CLI
- **Security (NFR12-14):** Credentials from env vars only, no secrets in state files or logs

**Scale & Complexity:**

- Primary domain: Python CLI / Developer Tooling
- Complexity level: Low (greenfield, single developer, no regulated domain)
- Estimated architectural components: ~5-7 (CLI parser, orchestrator, agent adapters, state manager, git handler, config loader, logger)

### Technical Constraints & Dependencies

- **Claude Agent SDK** required for Claude-based agents (SM, Reviewer)
- **GLM routing** via ANTHROPIC_BASE_URL for cost-efficient Dev agent
- **YAML format** for state persistence, inter-agent handoff, and user configuration (consistency over convention)
- **Git CLI** for branch/commit operations (not library-based)
- **uvx distribution** requires proper entry point and packaging

### Cross-Cutting Concerns Identified

1. **State Integrity:** Every phase must persist state atomically before proceeding
2. **Error Recovery:** Graceful pause on failure with clear messaging and resumable state
3. **Context Management:** Orchestrator must inject appropriate context without pollution
4. **Logging:** Structured, timestamped logs with handoff visibility for debugging
5. **Security Boundaries:** Credential isolation from state and logs

## Starter Template Evaluation

### Primary Technology Domain

Python CLI Tool (uvx-distributable) based on project requirements analysis.

### Starter Options Considered

| Option | Structure | Pros | Cons |
|--------|-----------|------|------|
| `uv init --package` | src/ layout + hatchling | Simple, matches PRD | Manual tooling setup |
| cookiecutter-uv | Full template | Pre-configured quality tools | Extra files |
| The Hatchlor | Hatch-focused | Deep hatch integration | Hatch-specific |

### Selected Starter: `uv init --package`

**Rationale for Selection:**
- Matches the PRD specification for uvx distribution
- Uses hatchling as already identified in technical research
- Minimal complexity appropriate for solo developer project
- Clean slate for adding project-specific dependencies

**Initialization Command:**

```bash
uv init --package --build-backend hatchling bmad-auto
cd bmad-auto
uv add typer[all] pyyaml claude-agent-sdk
```

### Architectural Decisions Provided by Starter

**Language & Runtime:**
- Python 3.11+ (modern async support)
- Type hints encouraged (Typer leverages them)

**Build System:**
- hatchling backend
- pyproject.toml-only configuration
- `[project.scripts]` entry point for CLI

**CLI Framework:**
- Typer for declarative command structure
- Rich integration for terminal output (via typer[all])
- Manual `asyncio.run()` wrapper for async commands

**Configuration Format:**
- YAML for all configuration (`.bmad-auto.yaml`)
- YAML for state persistence (`.bmad-auto-state.yaml`)
- YAML for inter-agent handoff files
- Rationale: Consistency across all project files over Python convention

**Project Structure:**
```
bmad-auto/
├── pyproject.toml
├── README.md
├── src/
│   └── bmad_auto/
│       ├── __init__.py
│       └── main.py      # CLI entry point
└── uv.lock
```

**Note:** Project initialization using this command should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

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

### Agent Orchestration

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

### Async Execution Model

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

### Logging Strategy

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

### Testing Strategy

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

### Decision Impact Analysis

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

## Implementation Patterns & Consistency Rules

**Reference:** All patterns MUST comply with `src/AGENTS.md` which defines authoritative Python development standards for this repository.

### Configuration Architecture

**Three-Layer Configuration (No Overlap):**

| Layer | File | Purpose | Loaded By |
|-------|------|---------|-----------|
| Internal defaults | pydantic_settings | Tool behavior, timeouts, retries | Tool initialization |
| User project config | `.bmad-auto.yaml` | Epic path, models, git settings | `uvx bmad-auto run` |
| Secrets | `.env` (no prefix) | `ANTHROPIC_API_KEY`, `ANTHROPIC_BASE_URL` | Environment/shell |

```python
# Internal defaults via pydantic_settings
class InternalSettings(BaseSettings):
    default_timeout: int = 600
    max_retries: int = 3

# User config loaded from .bmad-auto.yaml
@dataclass
class UserConfig:
    epic_path: str
    sm_model: str
    dev_model: str
    reviewer_model: str
    auto_branch: bool
    auto_commit: bool
    branch_prefix: str
```

### Project Structure (Vertical Slice per AGENTS.md)

```
src/bmad_auto/
├── __init__.py
├── main.py                      # CLI entry point (Typer)
├── shared/
│   ├── __init__.py
│   ├── consts.py                # All constants
│   ├── types.py                 # Shared type definitions
│   └── exceptions.py            # Domain exceptions
├── core/
│   ├── __init__.py
│   ├── orchestrator.py          # Main workflow logic
│   ├── state.py                 # YAML state persistence
│   ├── config.py                # Config loading (pydantic_settings + YAML)
│   └── tests/
│       ├── conftest.py
│       ├── test_orchestrator.py
│       ├── test_state.py
│       └── test_config.py
├── agents/
│   ├── __init__.py
│   ├── base.py                  # Agent protocol
│   ├── claude.py                # Claude Agent SDK wrapper
│   ├── prompts.py               # Prompt builders
│   └── tests/
│       ├── conftest.py
│       ├── test_claude.py
│       └── test_prompts.py
└── features/
    └── git_integration/
        ├── __init__.py
        ├── handler.py
        └── tests/
            └── test_handler.py
```

### Naming Patterns

**Python Code (per AGENTS.md/PEP 8):**
- Modules: `snake_case` (e.g., `state_manager.py`)
- Functions: `snake_case` (e.g., `run_story_loop()`)
- Classes: `PascalCase` (e.g., `WorkflowState`)
- Constants: `UPPER_SNAKE_CASE` in `shared/consts.py`

**YAML Keys:**
- `snake_case` for all keys (consistent with Python)

### Constants (per AGENTS.md §2.4)

All constants MUST live in `shared/consts.py`:

```python
# src/bmad_auto/shared/consts.py

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_PAUSED = 2
EXIT_CONFIG_ERROR = 3

# Agent identifiers
AGENT_SM = "sm"
AGENT_DEV = "dev"
AGENT_REVIEWER = "reviewer"

# Workflow phases
PHASE_SM = "sm"
PHASE_DEV = "dev"
PHASE_REVIEW = "review"

# Workflow statuses
STATUS_PENDING = "pending"
STATUS_IN_PROGRESS = "in_progress"
STATUS_PAUSED = "paused"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
```

### Logging Pattern (per AGENTS.md §8)

**structlog for logging, Rich for display:**

```python
import structlog

logger = structlog.get_logger(__name__)

# Structured log with context
logger.info("Agent handoff", from_agent=AGENT_SM, to_agent=AGENT_DEV, reason="story ready")
```

**Rich for user-facing display:**
```python
from rich.console import Console

console = Console()
console.print("[blue]SM:[/blue] Creating story 1 of 5...")
```

### Error Handling (per AGENTS.md §7)

**Domain exceptions in `shared/exceptions.py`:**

```python
class BmadAutoError(Exception):
    """Base exception for bmad-auto errors."""

class ConfigError(BmadAutoError):
    """Invalid or missing configuration."""

class StateCorruptionError(BmadAutoError):
    """State file corrupted or invalid."""

class AgentError(BmadAutoError):
    """Agent execution failed."""

class WorkflowPausedError(BmadAutoError):
    """Workflow paused due to recoverable error."""
```

### Git Commit Messages (per AGENTS.md §13.2)

Semantic commit format:
```
feat(orchestrator): add story loop execution
fix(state): handle corrupted YAML gracefully
refactor(agents): extract prompt builder
test(orchestrator): add integration tests
```

### State File Format

```yaml
# .bmad-auto-state.yaml
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

### Code Limits (per AGENTS.md §2.2)

- Files: ≤500 lines
- Functions: ≤50 lines
- Classes: ≤100 lines
- Line length: 100 characters

### Testing Rules (per AGENTS.md §9)

- Tests co-located in `tests/` subdirectories
- `conftest.py` for shared fixtures
- 80% minimum coverage
- pytest only (no unittest)
- Mock external dependencies

### Enforcement Summary

**All AI Agents MUST:**
1. Follow `src/AGENTS.md` as the authoritative standard
2. Use absolute imports from `bmad_auto.*`
3. Place constants in `shared/consts.py`
4. Use structlog for logging, Rich for display
5. Define domain exceptions, no bare `except Exception`
6. Use semantic commit messages
7. Co-locate tests with features
8. Maintain 80% test coverage

