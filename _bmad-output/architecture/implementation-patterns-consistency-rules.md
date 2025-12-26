# Implementation Patterns & Consistency Rules

**Reference:** All patterns MUST comply with `src/AGENTS.md` which defines authoritative Python development standards for this repository.

## Configuration Architecture

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

## Project Structure (Vertical Slice per AGENTS.md)

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

## Naming Patterns

**Python Code (per AGENTS.md/PEP 8):**
- Modules: `snake_case` (e.g., `state_manager.py`)
- Functions: `snake_case` (e.g., `run_story_loop()`)
- Classes: `PascalCase` (e.g., `WorkflowState`)
- Constants: `UPPER_SNAKE_CASE` in `shared/consts.py`

**YAML Keys:**
- `snake_case` for all keys (consistent with Python)

## Constants (per AGENTS.md §2.4)

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

## Logging Pattern (per AGENTS.md §8)

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

## Error Handling (per AGENTS.md §7)

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

## Git Commit Messages (per AGENTS.md §13.2)

Semantic commit format:
```
feat(orchestrator): add story loop execution
fix(state): handle corrupted YAML gracefully
refactor(agents): extract prompt builder
test(orchestrator): add integration tests
```

## State File Format

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

## Code Limits (per AGENTS.md §2.2)

- Files: ≤500 lines
- Functions: ≤50 lines
- Classes: ≤100 lines
- Line length: 100 characters

## Testing Rules (per AGENTS.md §9)

- Tests co-located in `tests/` subdirectories
- `conftest.py` for shared fixtures
- 80% minimum coverage
- pytest only (no unittest)
- Mock external dependencies

## Enforcement Summary

**All AI Agents MUST:**
1. Follow `src/AGENTS.md` as the authoritative standard
2. Use absolute imports from `bmad_auto.*`
3. Place constants in `shared/consts.py`
4. Use structlog for logging, Rich for display
5. Define domain exceptions, no bare `except Exception`
6. Use semantic commit messages
7. Co-locate tests with features
8. Maintain 80% test coverage
