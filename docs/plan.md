# Implementation Plan: bmad-auto CLI Tool

**Project**: bmad-auto - BMAD Methodology Automation CLI
**Location**: /home/warm/Dropbox/Public/WORKs/Python/coding_workflow
**Branch**: mvp-cli

---

## Progress Checkpoint (2025-12-21)

- Implemented resume_workflow in orchestrator with skipping completed stories.
- Expanded CLI with init/run/resume/status/list_epics/config_validate plus dry-run.
- Added headless reporter and basic Textual TUI scaffolding.
- Added resume workflow test coverage.

## Progress Checkpoint (2025-12-21)

- Orchestrator expanded: add-context, retrospective, documentation, and create-PR phases implemented with optional templates.
- Fixed branch/commit prefixing to avoid double-prefixing in the workflow engine.
- Story flow now validates after optional context expansion.
- Added default prompt templates for create_story, add_context, develop, code_review, retrospective, documentation, and create_pr.
- Remaining: expand CLI commands, TUI, templates, README, CI.

## Progress Checkpoint (2025-12-20)

- Phase 6 Orchestrator started: added phases enum, prompt loader, and workflow engine with story runner.
- Added orchestrator tests for prompt rendering and engine success/rejection flows.
- Added shared constants for templates, roles, and story id validation.
- Remaining: finish orchestrator (context/doc/PR phases), expand CLI commands, TUI, templates, README, CI.

## Progress Checkpoint (2025-12-18)

- Phase 1 scaffolding completed: `pyproject.toml`, package layout, `.python-version`, `.gitignore` updated.
- Core modules implemented: `shared/consts.py`, `core/exceptions.py`, `core/protocols.py`, `core/config.py`,
  `core/logging.py`, `core/__init__.py`, `shared/__init__.py`, `shared/utils/__init__.py`.
- CLI entrypoints added: `main.py`, `cli.py` with version and config_show commands plus logging bootstrap.
- Tests added and passing: constants, exceptions, logging level, settings defaults and YAML override.
- Phase 2 Agent Layer DONE: models, base agent, Claude/Codex wrappers, factory, and tests (17/17 passing).
- Phase 3 State & Git DONE: state models/manager, git models/manager implemented with tests (9/9 passing).
- Phase 4 Discovery nearing completion: added discovery models, epic/story parsers, epic discovery finder, and tests (6/6 passing). Remaining: wire discovery into orchestrator and add edge-case parser coverage.

---

## Overview

Build a uvx-installable CLI tool that automates the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology by orchestrating Claude Code and Codex CLI tools.

---

## Phase 1: Project Scaffolding

### 1.1 Create pyproject.toml
**File**: `pyproject.toml`
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "bmad-auto"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "typer>=0.15.0",
  "rich>=13.9.0",
  "textual>=1.0.0",
  "pydantic>=2.10.0",
  "pydantic-settings>=2.6.0",
  "gitpython>=3.1.0",
  "tenacity>=9.0.0",
  "structlog>=24.4.0",
  "pyyaml>=6.0",
]

[project.scripts]
bmad-auto = "bmad_auto.main:main"

[dependency-groups]
dev = ["pytest>=8.3.0", "pytest-cov>=6.0.0", "pytest-asyncio>=0.24.0", "ruff>=0.8.0", "pyright>=1.1.390"]
```

### 1.2 Create Package Structure
```
src/bmad_auto/
├── __init__.py           # Version and exports
├── main.py               # Entry point (<20 lines)
├── cli.py                # Typer CLI commands
├── core/
│   ├── __init__.py
│   ├── config.py         # pydantic-settings configuration
│   ├── exceptions.py     # Custom exception hierarchy
│   ├── protocols.py      # Protocol definitions for DI
│   ├── logging.py        # structlog setup
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_*.py
├── features/
│   ├── agents/
│   ├── orchestrator/
│   ├── git_ops/
│   ├── state/
│   ├── discovery/
│   └── tui/
├── shared/
│   ├── __init__.py
│   ├── consts.py         # All constants
│   ├── types.py          # Type aliases
│   └── utils/
└── templates/            # Prompt templates
```

### 1.3 Create Supporting Files
- `.python-version` → `3.13`
- `.gitignore` updates for `.bmad-auto/state/`

---

## Phase 2: Core Infrastructure

### 2.1 Constants Module
**File**: [shared/consts.py](src/bmad_auto/shared/consts.py)
- `CLI_CLAUDE = "claude"`
- `CLI_CODEX = "codex"`
- `DEFAULT_STATE_DIR = ".bmad-auto/state"`
- `DEFAULT_CONFIG_FILE = ".bmad-auto/config.yaml"`
- `MAX_DEV_ATTEMPTS = 3`
- `DEFAULT_AGENT_TIMEOUT = 600`
- `MARKER_NO_MORE_STORIES = "NO_MORE_STORIES"`
- `MARKER_REVIEW_APPROVED = "APPROVED"`
- `MARKER_REVIEW_REJECTED = "REJECTED"`

### 2.2 Exception Hierarchy
**File**: [core/exceptions.py](src/bmad_auto/core/exceptions.py)
```python
class BmadAutoError(Exception): ...
class ConfigurationError(BmadAutoError): ...
class AgentNotFoundError(BmadAutoError): ...
class AgentExecutionError(BmadAutoError): ...
class AgentTimeoutError(BmadAutoError): ...
class AgentOutputParseError(BmadAutoError): ...
class WorkflowError(BmadAutoError): ...
class EpicNotFoundError(WorkflowError): ...
class StoryCreationError(WorkflowError): ...
class ReviewRejectedError(WorkflowError): ...
class GitOperationError(BmadAutoError): ...
class StateError(BmadAutoError): ...
```

### 2.3 Protocol Definitions
**File**: [core/protocols.py](src/bmad_auto/core/protocols.py)
```python
class AgentProtocol(Protocol):
    async def run(self, prompt: str, session_id: str | None = None) -> AgentResult: ...
    def validate(self) -> None: ...

class StateManagerProtocol(Protocol):
    def load(self, workflow_id: str) -> WorkflowState | None: ...
    def save(self, state: WorkflowState) -> None: ...
    def list_all(self) -> list[WorkflowState]: ...

class GitManagerProtocol(Protocol):
    def create_branch(self, name: str) -> None: ...
    def commit(self, message: str) -> None: ...
    def push_and_create_pr(self, title: str, body: str) -> str: ...

class ProgressReporterProtocol(Protocol):
    def on_phase_start(self, phase: str, story_id: str | None) -> None: ...
    def on_agent_start(self, role: str) -> None: ...
    def on_complete(self, success: bool) -> None: ...
```

### 2.4 Configuration System
**File**: [core/config.py](src/bmad_auto/core/config.py)
- Use pydantic-settings with `BMAD_` prefix
- Load from: CLI args → env vars → repo config → user config → defaults
- Settings groups: `scrum_master`, `developer`, `reviewer`, `tech_writer`, `git`, `workflow`, `discovery`

### 2.5 Logging Setup
**File**: [core/logging.py](src/bmad_auto/core/logging.py)
- Configure structlog with format per AGENTS.md
- No print statements in production

---

## Phase 3: Agent Layer

### 3.1 Agent Models
**File**: [features/agents/models.py](src/bmad_auto/features/agents/models.py)
```python
class AgentConfig(BaseModel):
    cli: Literal["claude", "codex"]
    settings_file: Path | None = None
    working_dir: Path = Path(".")
    timeout: int = 600
    extra_args: list[str] = []

class AgentResult(BaseModel):
    success: bool
    output: str
    error: str | None = None
    session_id: str | None = None
    cost_usd: float | None = None
    duration_seconds: float
```

### 3.2 Base Agent
**File**: [features/agents/base.py](src/bmad_auto/features/agents/base.py)
- Abstract base with subprocess execution
- Validate CLI exists via `shutil.which`
- Async subprocess with timeout
- Capture stdout/stderr
- Parse output to AgentResult

### 3.3 Claude Agent
**File**: [features/agents/claude.py](src/bmad_auto/features/agents/claude.py)
- Command: `claude -p <prompt> --output-format json`
- Parse JSON: `result`, `session_id`, `total_cost_usd`
- Resume: `--resume <session_id>`

### 3.4 Codex Agent
**File**: [features/agents/codex.py](src/bmad_auto/features/agents/codex.py)
- Command: `codex exec --json --config <path> <prompt>`
- Parse JSONL: look for `turn.completed`, `agent_message`
- Resume: `codex exec resume --last`

### 3.5 Agent Factory
**File**: [features/agents/factory.py](src/bmad_auto/features/agents/factory.py)
```python
def create_agent(config: AgentConfig) -> AgentProtocol: ...
```

---

## Phase 4: State and Git

### 4.1 State Models
**File**: [features/state/models.py](src/bmad_auto/features/state/models.py)
```python
class WorkflowState(BaseModel):
    workflow_id: str
    epic_file: str
    status: Literal["pending", "running", "paused", "failed", "completed"]
    branch_name: str | None = None
    current_phase: str
    current_story: str | None = None
    completed_stories: list[str] = []
    failed_stories: list[str] = []
    error: str | None = None
    started_at: datetime
    updated_at: datetime

class StoryContext(BaseModel):
    story_id: str
    story_file: str
    dev_attempts: int = 0
    review_passed: bool = False
```

### 4.2 State Manager
**File**: [features/state/manager.py](src/bmad_auto/features/state/manager.py)
- Save/load JSON files in `.bmad-auto/state/`
- List all workflows
- Auto-update timestamps

### 4.3 Git Models
**File**: [features/git_ops/models.py](src/bmad_auto/features/git_ops/models.py)
```python
class GitConfig(BaseModel):
    branch_prefix: str = "bmad"
    commit_prefix: str = "feat(bmad):"
    auto_push: bool = False
    create_pr: bool = True
    pr_draft: bool = True
```

### 4.4 Git Manager
**File**: [features/git_ops/manager.py](src/bmad_auto/features/git_ops/manager.py)
- Use GitPython for branch/commit operations
- Use `gh` CLI for PR creation
- Branch naming: `<prefix>/<epic_id>`

---

## Phase 5: Discovery

### 5.1 Discovery Models
**File**: [features/discovery/models.py](src/bmad_auto/features/discovery/models.py)
```python
class EpicInfo(BaseModel):
    id: str
    title: str
    description: str
    story_refs: list[str]
    dependencies: list[str]
    file_path: Path

class StoryInfo(BaseModel):
    id: str
    title: str
    context: str
    acceptance_criteria: list[str]
    checklist: list[str]
    file_path: Path
```

### 5.2 Epic Parser
**File**: [features/discovery/epic_parser.py](src/bmad_auto/features/discovery/epic_parser.py)
- Parse epic markdown files
- Extract stories, dependencies, acceptance criteria

### 5.3 Story Parser
**File**: [features/discovery/story_parser.py](src/bmad_auto/features/discovery/story_parser.py)
- Parse story markdown files
- Extract context, acceptance criteria, checklist

---

## Phase 6: Orchestrator

### 6.1 Phase Definitions
**File**: [features/orchestrator/phases.py](src/bmad_auto/features/orchestrator/phases.py)
```python
class Phase(StrEnum):
    CREATE_BRANCH = "create_branch"
    CREATE_STORY = "create_story"
    VALIDATE_STORY = "validate_story"
    ADD_CONTEXT = "add_context"
    DEVELOP = "develop"
    CODE_REVIEW = "code_review"
    COMMIT = "commit"
    RETROSPECTIVE = "retrospective"
    DOCUMENTATION = "documentation"
    CREATE_PR = "create_pr"
```

### 6.2 Prompt Templates
**File**: [features/orchestrator/prompts.py](src/bmad_auto/features/orchestrator/prompts.py)
- Template loading from `templates/` directory
- Variable substitution for each phase

### 6.3 Workflow Engine
**File**: [features/orchestrator/engine.py](src/bmad_auto/features/orchestrator/engine.py)
- Main orchestration loop
- Phase transitions based on results
- Retry logic for DEVELOP/CODE_REVIEW
- State persistence after each phase
- Progress reporting callbacks

---

## Phase 7: CLI

### 7.1 CLI Commands
**File**: [cli.py](src/bmad_auto/cli.py)
```python
app = typer.Typer()

@app.command()
def init(repo_path: Path = ...) -> None: ...

@app.command()
def run(epic: Path = ..., tui: bool = False, dry_run: bool = False) -> None: ...

@app.command()
def resume(workflow_id: str = ...) -> None: ...

@app.command()
def status(repo_path: Path = ...) -> None: ...

@app.command()
def list_epics(repo_path: Path = ...) -> None: ...

@app.command()
def config_validate(repo_path: Path = ...) -> None: ...

@app.command()
def config_show(repo_path: Path = ...) -> None: ...
```

### 7.2 Main Entry Point
**File**: [main.py](src/bmad_auto/main.py)
```python
def main() -> None:
    from bmad_auto.cli import app
    app()
```

---

## Phase 8: TUI

### 8.1 Headless Reporter
**File**: [features/tui/headless.py](src/bmad_auto/features/tui/headless.py)
- Rich console output for non-TUI mode
- Progress bars and status tables

### 8.2 TUI Widgets
**File**: [features/tui/widgets.py](src/bmad_auto/features/tui/widgets.py)
- `WorkflowStatusWidget`
- `StoryTableWidget`
- `AgentLogWidget`
- `ControlsWidget`

### 8.3 TUI Application
**File**: [features/tui/app.py](src/bmad_auto/features/tui/app.py)
- Main Textual app
- Keybindings: q (quit), p (pause), r (resume), s (skip)

---

## Testing Strategy

### Test Coverage Target: 80%

### Unit Tests (co-located)
Each feature module has `tests/` subdirectory:
- Mock all subprocess calls
- Mock file system with `tmp_path`
- Mock git operations

### Key Test Files
- `core/tests/test_config.py` - Configuration loading
- `core/tests/test_exceptions.py` - Exception hierarchy
- `features/agents/tests/test_claude.py` - Claude subprocess
- `features/agents/tests/test_codex.py` - Codex subprocess
- `features/state/tests/test_manager.py` - State persistence
- `features/git_ops/tests/test_manager.py` - Git operations
- `features/orchestrator/tests/test_engine.py` - Workflow logic

### Fixtures (conftest.py)
- `agent_config` - Default AgentConfig
- `workflow_state` - Default WorkflowState
- `temp_repo` - Temporary git repository
- `mock_claude_success` - Mock successful Claude
- `mock_codex_success` - Mock successful Codex

---

## Implementation Order (Critical Path)

```
Week 1: Foundation
├── pyproject.toml, package structure
├── shared/consts.py
├── core/exceptions.py
├── core/protocols.py
├── core/config.py + tests
└── core/logging.py

Week 2: Agents
├── features/agents/models.py
├── features/agents/base.py + tests
├── features/agents/claude.py + tests
├── features/agents/codex.py + tests
└── features/agents/factory.py

Week 3: State & Git
├── features/state/models.py
├── features/state/manager.py + tests
├── features/git_ops/models.py
└── features/git_ops/manager.py + tests

Week 4: Discovery & Orchestrator
├── features/discovery/models.py
├── features/discovery/epic_parser.py + tests
├── features/discovery/story_parser.py + tests
├── features/orchestrator/phases.py
├── features/orchestrator/prompts.py
└── features/orchestrator/engine.py + tests

Week 5: CLI & TUI
├── cli.py + tests
├── main.py
├── features/tui/headless.py
├── features/tui/widgets.py
└── features/tui/app.py

Week 6: Polish
├── templates/ (prompt files)
├── README.md
├── CI configuration
└── Final coverage check
```

---

## Files to Create (Summary)

| File | Lines (est) | Priority |
|------|-------------|----------|
| `pyproject.toml` | 50 | P0 |
| `src/bmad_auto/__init__.py` | 10 | P0 |
| `src/bmad_auto/main.py` | 15 | P0 |
| `src/bmad_auto/shared/consts.py` | 40 | P0 |
| `src/bmad_auto/core/exceptions.py` | 80 | P0 |
| `src/bmad_auto/core/protocols.py` | 100 | P0 |
| `src/bmad_auto/core/config.py` | 200 | P0 |
| `src/bmad_auto/core/logging.py` | 50 | P0 |
| `src/bmad_auto/features/agents/models.py` | 50 | P1 |
| `src/bmad_auto/features/agents/base.py` | 150 | P1 |
| `src/bmad_auto/features/agents/claude.py` | 100 | P1 |
| `src/bmad_auto/features/agents/codex.py` | 100 | P1 |
| `src/bmad_auto/features/state/models.py` | 60 | P1 |
| `src/bmad_auto/features/state/manager.py` | 100 | P1 |
| `src/bmad_auto/features/git_ops/models.py` | 30 | P1 |
| `src/bmad_auto/features/git_ops/manager.py` | 150 | P1 |
| `src/bmad_auto/features/discovery/models.py` | 50 | P2 |
| `src/bmad_auto/features/discovery/epic_parser.py` | 100 | P2 |
| `src/bmad_auto/features/discovery/story_parser.py` | 80 | P2 |
| `src/bmad_auto/features/orchestrator/phases.py` | 30 | P2 |
| `src/bmad_auto/features/orchestrator/prompts.py` | 80 | P2 |
| `src/bmad_auto/features/orchestrator/engine.py` | 300 | P2 |
| `src/bmad_auto/cli.py` | 200 | P3 |
| `src/bmad_auto/features/tui/headless.py` | 100 | P3 |
| `src/bmad_auto/features/tui/widgets.py` | 200 | P3 |
| `src/bmad_auto/features/tui/app.py` | 150 | P3 |

---

## Research Documentation Created

- [docs/research/claude-code-cli-reference.md](docs/research/claude-code-cli-reference.md)
- [docs/research/codex-cli-reference.md](docs/research/codex-cli-reference.md)
- [docs/research/bmad-methodology.md](docs/research/bmad-methodology.md)

---

## Key Technical Decisions

1. **Async subprocess execution** - Use `asyncio.create_subprocess_exec` for agent invocation
2. **JSON output parsing** - Claude uses `--output-format json`, Codex uses `--json` (JSONL)
3. **State persistence** - JSON files in `.bmad-auto/state/`
4. **Git operations** - GitPython for local ops, `gh` CLI for PRs
5. **TUI framework** - Textual for full TUI, Rich for headless mode
6. **DI via Protocols** - All major components are protocol-based for testability
