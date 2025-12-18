****# bmad-auto: Comprehensive Design Document

**Version:** 1.0.0  
**Date:** December 2025  
**Purpose:** Complete specification for implementation in a separate session

---

## Executive Summary

`bmad-auto` is a **uvx-installable CLI tool** that automates the implementation phase of the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology. It orchestrates Claude Code CLI and OpenAI Codex CLI tools to execute story-driven development loops with different agent configurations (tiers) for different roles.

**Core Philosophy:**
- Pure Python orchestrator with subprocess-based CLI execution
- Rich terminal UI for live progress visualization (no external dashboard server required)
- Callable from any repository as an external tool
- State persistence per-repository
- Strict adherence to Python 3.13+ standards and vertical slice architecture

---

## 1. Problem Statement

### 1.1 Current BMAD Workflow Pain Points

The BMAD methodology defines a structured workflow for AI-driven development with specialized agents (Scrum Master, Developer, Reviewer, Tech Writer). Currently, this workflow requires manual orchestration:

1. Manually invoking Claude Code or Codex CLI with different settings for each role
2. Manually managing git branches and commits between story completions
3. Manually tracking which stories are complete, failed, or pending
4. Manually copying context between agent invocations
5. No visibility into overall workflow progress

### 1.2 Solution Requirements

`bmad-auto` must:

1. **Orchestrate CLI agents** - Invoke Claude Code and Codex CLI with role-specific configurations
2. **Manage workflow state** - Track progress through epic/story loops with persistence
3. **Handle git operations** - Create branches, commit changes, create PRs automatically
4. **Provide visibility** - Show real-time progress via terminal UI
5. **Be portable** - Installable via `uvx`, callable from any repository
6. **Be resumable** - Support pausing and resuming workflows
7. **Follow strict Python standards** - Comply with src/AGENTS.md guidelines

---

## 2. Architecture Overview

### 2.1 High-Level Design

The system follows a **vertical slice architecture** with clear separation of concerns:

```
bmad-auto (external tool)
    │
    ├── CLI Layer (Typer)
    │   └── Commands: init, run, status, resume, list
    │
    ├── Orchestrator Layer
    │   └── Workflow engine with phase-based execution
    │
    ├── Agent Layer
    │   └── CLI wrappers for Claude Code and Codex
    │
    ├── Infrastructure Layer
    │   ├── State persistence (JSON files)
    │   ├── Git operations (GitPython + gh CLI)
    │   └── Configuration (pydantic-settings)
    │
    └── TUI Layer (Textual/Rich)
        └── Terminal dashboard and progress reporting
```

### 2.2 Execution Model

The orchestrator runs **locally on the user's machine** as a CLI tool. It:

1. Discovers epic files from the target repository
2. Creates a feature branch for the epic
3. Loops through stories, invoking CLI agents via subprocess
4. Persists state to `.bmad-auto/` in the target repository
5. Creates a PR when the epic is complete

**No external services are required** - everything runs in the terminal, including the optional TUI dashboard.

### 2.3 Dependency Injection Strategy

All major components are defined as **Protocols** (abstract interfaces) and injected into the orchestrator:

- `AgentProtocol` - For CLI agent implementations
- `StateManagerProtocol` - For state persistence
- `GitManagerProtocol` - For git operations

This enables:
- Easy testing with mock implementations
- Swapping implementations without changing orchestrator logic
- Clear contracts between components

---

## 3. Project Structure

### 3.1 Package Layout (Vertical Slice)

The project follows vertical slice architecture with tests co-located by feature:

```
bmad-auto/
├── pyproject.toml                 # hatchling build, uv dependencies
├── uv.lock                        # Locked dependencies
├── .python-version                # 3.13
├── README.md
│
├── src/
│   └── bmad_auto/
│       ├── __init__.py            # Package version, exports
│       ├── main.py                # Entry point (< 20 lines)
│       ├── cli.py                 # Typer CLI definitions (< 200 lines)
│       │
│       ├── core/                  # Shared infrastructure
│       │   ├── __init__.py
│       │   ├── config.py          # pydantic-settings configuration
│       │   ├── exceptions.py      # All custom exceptions
│       │   ├── protocols.py       # Protocol definitions for DI
│       │   ├── logging.py         # structlog configuration
│       │   └── tests/
│       │       ├── __init__.py
│       │       ├── conftest.py
│       │       ├── test_config.py
│       │       └── test_exceptions.py
│       │
│       ├── features/              # Feature modules (vertical slices)
│       │   ├── agents/            # CLI agent wrappers
│       │   ├── orchestrator/      # Workflow engine
│       │   ├── git_ops/           # Git operations
│       │   ├── state/             # State persistence
│       │   ├── discovery/         # Epic/story file parsing
│       │   └── tui/               # Terminal UI
│       │
│       └── shared/                # Shared utilities
│           ├── __init__.py
│           ├── consts.py          # All magic values as constants
│           ├── types.py           # Type aliases
│           └── utils/
│               ├── __init__.py
│               ├── subprocess_utils.py
│               └── tests/
│
└── templates/                     # Default config templates (non-Python)
    ├── config.yaml
    ├── claude_high.json
    ├── claude_low.json
    ├── codex_high.toml
    └── codex_low.toml
```

### 3.2 Feature Module Structure

Each feature follows the same internal structure:

```
features/<feature_name>/
├── __init__.py          # Public exports
├── models.py            # Pydantic models for this feature
├── <primary>.py         # Main implementation (< 500 lines)
├── <secondary>.py       # Additional implementation if needed
└── tests/
    ├── __init__.py
    ├── conftest.py      # Shared fixtures for this feature
    └── test_<module>.py # Test files matching source files
```

### 3.3 File Size Constraints

Per AGENTS.md guidelines:
- **Files:** Maximum 500 lines
- **Functions:** Maximum 50 lines
- **Classes:** Maximum 100 lines
- **Line length:** Maximum 100 characters

When approaching limits, split into smaller modules with clear single responsibilities.

---

## 4. Core Module Specifications

### 4.1 Configuration System

**Location:** `core/config.py`

**Design:**
- Uses `pydantic-settings` for configuration management
- Loads from environment variables with `BMAD_` prefix
- Supports `.env` file loading
- Supports YAML config file override
- All settings validated via Pydantic

**Configuration Hierarchy (highest to lowest priority):**
1. CLI arguments
2. Environment variables (`BMAD_*`)
3. Repository config (`.bmad-auto/config.yaml`)
4. User config (`~/.config/bmad-auto/config.yaml`)
5. Built-in defaults

**Settings Structure:**

| Setting Group | Purpose |
|---------------|---------|
| `scrum_master` | Agent config for story creation, retrospective |
| `developer` | Agent config for implementation |
| `reviewer` | Agent config for code review |
| `tech_writer` | Agent config for documentation |
| `git` | Git operation settings (branch prefix, PR options) |
| `workflow` | Workflow behavior (max retries, pause points) |
| `discovery` | Epic/story file patterns |
| `state_dir` | Where to store workflow state |
| `log_level` | Logging verbosity |

**Agent Settings Fields:**
- `cli`: Which CLI tool ("claude" or "codex")
- `settings_file`: Path to CLI-specific settings (JSON for Claude, TOML for Codex)
- `timeout`: Maximum execution time in seconds
- `extra_args`: Additional CLI arguments to pass

### 4.2 Exception Hierarchy

**Location:** `core/exceptions.py`

**Design:**
- All exceptions inherit from `BmadAutoError` base class
- Specific exceptions for each failure mode
- Exceptions carry context (cli name, timeout value, etc.)
- No silent fallbacks - all errors are explicit

**Exception Classes:**

| Exception | When Raised |
|-----------|-------------|
| `BmadAutoError` | Base class for all errors |
| `ConfigurationError` | Invalid or missing configuration |
| `AgentNotFoundError` | CLI tool not found in PATH |
| `AgentExecutionError` | CLI tool returned non-zero exit code |
| `AgentTimeoutError` | CLI tool exceeded timeout |
| `AgentOutputParseError` | Failed to parse CLI JSON output |
| `WorkflowError` | Base for workflow errors |
| `EpicNotFoundError` | Epic file does not exist |
| `StoryCreationError` | Failed to create story from epic |
| `ReviewRejectedError` | Code review failed after max attempts |
| `GitOperationError` | Git command failed |
| `StateError` | State persistence failed |

### 4.3 Protocol Definitions

**Location:** `core/protocols.py`

**Design:**
- Protocols define interfaces for dependency injection
- No implementation details, only method signatures
- Enables testing with mock implementations

**Protocols:**

| Protocol | Purpose | Key Methods |
|----------|---------|-------------|
| `AgentProtocol` | CLI agent interface | `run(prompt, session_id) -> AgentResult`, `validate()` |
| `StateManagerProtocol` | State persistence | `load(id)`, `save(state)`, `list_all()` |
| `GitManagerProtocol` | Git operations | `create_branch()`, `commit()`, `push_and_create_pr()` |
| `ProgressReporterProtocol` | Progress callbacks | `on_phase_start()`, `on_agent_start()`, `on_complete()` |

### 4.4 Logging Configuration

**Location:** `core/logging.py`

**Design:**
- Uses `structlog` for structured logging
- Configurable output format (JSON for production, pretty for dev)
- Log format includes: timestamp, level, module, function, line number, message
- No `print` statements anywhere in production code

**Log Levels:**
- `DEBUG`: Detailed execution flow, CLI commands being run
- `INFO`: Phase transitions, agent completions, story completions
- `WARNING`: Retryable failures, slow operations
- `ERROR`: Unrecoverable failures, exceptions

---

## 5. Feature Module Specifications

### 5.1 Agents Feature

**Location:** `features/agents/`

**Purpose:** Wrap Claude Code and Codex CLI tools as async Python interfaces.

**Models:**

| Model | Purpose | Fields |
|-------|---------|--------|
| `AgentConfig` | Configuration for agent instance | `cli`, `settings_file`, `working_dir`, `timeout`, `extra_args` |
| `AgentResult` | Result from agent execution | `success`, `output`, `error`, `session_id`, `cost_usd`, `duration_seconds` |

**Components:**

| Component | Purpose |
|-----------|---------|
| `BaseAgent` | Abstract base class with shared subprocess logic |
| `ClaudeAgent` | Claude Code CLI wrapper |
| `CodexAgent` | Codex CLI wrapper |
| `create_agent()` | Factory function to create agent from config |

**BaseAgent Responsibilities:**
- Validate CLI tool exists in PATH (using `shutil.which`)
- Build command line arguments
- Execute subprocess with timeout (using `asyncio.create_subprocess_exec`)
- Capture stdout/stderr
- Parse output into `AgentResult`
- Log execution timing and results

**ClaudeAgent Specifics:**
- CLI command: `claude`
- Output format: `--output-format json`
- Headless mode: `-p` flag for print mode
- Session resume: `--resume <session_id>`
- Output parsing: JSON with `result`, `session_id`, `total_cost_usd` fields

**CodexAgent Specifics:**
- CLI command: `codex exec`
- Output format: `--json` flag for JSONL streaming
- Config file: `--config <path>` for TOML config
- Session resume: `resume --last`
- Output parsing: JSONL stream, look for `task.completed` event

**Error Handling:**
- `AgentNotFoundError` if CLI not in PATH
- `AgentTimeoutError` if execution exceeds timeout
- `AgentExecutionError` if non-zero exit code
- `AgentOutputParseError` if JSON parsing fails

### 5.2 State Feature

**Location:** `features/state/`

**Purpose:** Persist workflow state to enable pause/resume functionality.

**Models:**

| Model | Purpose | Fields |
|-------|---------|--------|
| `WorkflowState` | Complete workflow state | `workflow_id`, `epic_file`, `status`, `branch_name`, `current_phase`, `current_story`, `completed_stories`, `failed_stories`, `error`, `started_at`, `updated_at` |
| `StoryContext` | Context for current story | `story_id`, `story_file`, `dev_attempts`, `review_passed` |

**Workflow Status Values:**
- `pending`: Created but not started
- `running`: Currently executing
- `paused`: Manually paused by user
- `failed`: Unrecoverable error occurred
- `completed`: All stories finished successfully

**StateManager Responsibilities:**
- Create state directory if not exists
- Save state as JSON file (one file per workflow)
- Load state by workflow ID
- List all persisted workflows
- Update timestamps on save

**File Location:**
- State stored in `.bmad-auto/state/` within target repository
- Filename: `<workflow_id>.json`
- Git-ignored (add to `.gitignore` during init)

### 5.3 Git Operations Feature

**Location:** `features/git_ops/`

**Purpose:** Manage git branching, commits, and PR creation.

**Models:**

| Model | Purpose | Fields |
|-------|---------|--------|
| `GitConfig` | Git operation settings | `branch_prefix`, `commit_prefix`, `auto_push`, `create_pr`, `pr_draft` |

**GitManager Responsibilities:**
- Create feature branch from base (default: main)
- Stage all changes (modified + untracked)
- Commit with formatted message
- Get diff (staged or unstaged)
- Push branch to remote
- Create PR using GitHub CLI (`gh pr create`)

**Branch Naming:**
- Format: `<prefix>/<epic_id>`
- Example: `bmad/epic-001`

**Commit Message Format:**
- Format: `<prefix> <story_id>: <summary>`
- Example: `feat(bmad): STORY-001 implement user authentication`

**PR Creation:**
- Uses `gh` CLI (GitHub CLI)
- Creates draft PR by default
- Auto-generates body with completed/failed story list

**Error Handling:**
- `GitOperationError` with operation name and error message
- Validate git repository exists before operations
- Validate `gh` CLI exists before PR creation

### 5.4 Discovery Feature

**Location:** `features/discovery/`

**Purpose:** Find and parse BMAD epic/story files from target repository.

**Components:**

| Component | Purpose |
|-----------|---------|
| `EpicDiscovery` | Find epic files matching patterns |
| `EpicParser` | Parse epic markdown into structured data |
| `StoryParser` | Parse story markdown into structured data |

**Epic Discovery:**
- Search patterns configurable (default: `docs/epics/*.md`, `docs/epics/**/*.md`)
- Return list of Path objects
- Filter already-processed epics based on state

**Epic File Structure (BMAD format):**
- Title and description
- List of stories (may be high-level or detailed)
- Acceptance criteria
- Dependencies on other epics
- Technical context references

**Story File Structure (BMAD format):**
- Story ID and title
- Full implementation context
- Acceptance criteria (Gherkin-style preferred)
- Technical notes from architecture
- Checklist of subtasks

**Output Models:**

| Model | Purpose | Fields |
|-------|---------|--------|
| `EpicInfo` | Parsed epic metadata | `id`, `title`, `description`, `story_refs`, `dependencies` |
| `StoryInfo` | Parsed story metadata | `id`, `title`, `context`, `acceptance_criteria`, `checklist` |

### 5.5 Orchestrator Feature

**Location:** `features/orchestrator/`

**Purpose:** Execute the BMAD workflow by coordinating agents, state, and git.

**Models:**

| Model | Purpose | Fields |
|-------|---------|--------|
| `Phase` | Enum of workflow phases | `CREATE_BRANCH`, `CREATE_STORY`, `DEVELOP`, `CODE_REVIEW`, `RETROSPECTIVE`, etc. |
| `PhaseResult` | Result of phase execution | `phase`, `success`, `output`, `next_phase` |

**Workflow Phases:**

| Phase | Agent | Tier | Description |
|-------|-------|------|-------------|
| `CREATE_BRANCH` | N/A | N/A | Create git branch for epic |
| `CREATE_STORY` | Scrum Master | High | Generate next story from epic |
| `VALIDATE_STORY` | Scrum Master | High | Optional validation of story quality |
| `ADD_CONTEXT` | Scrum Master | High | Add context if story needs more detail |
| `DEVELOP` | Developer | Low | Implement the story |
| `CODE_REVIEW` | Reviewer | High | Review implementation |
| `COMMIT` | N/A | N/A | Commit changes to git |
| `RETROSPECTIVE` | Scrum Master | High | Review completed stories |
| `DOCUMENTATION` | Tech Writer | High | Generate/update documentation |
| `CREATE_PR` | N/A | N/A | Push and create pull request |

**Orchestrator Responsibilities:**
- Load or create workflow state
- Iterate through phases in order
- Handle phase transitions based on results
- Invoke appropriate agent for each phase
- Manage retry logic for failed phases
- Persist state after each phase
- Report progress via callback

**Story Loop Logic:**

```
FOR each story in epic:
    1. CREATE_STORY (scrum master) -> story file
    2. IF story needs context:
         ADD_CONTEXT (scrum master) -> updated story
    3. DEVELOPMENT LOOP (max N attempts):
         a. DEVELOP (developer) -> code changes
         b. CODE_REVIEW (reviewer) -> pass/fail
         c. IF pass: break loop
         d. IF fail: continue loop with feedback
    4. IF all attempts failed: mark story failed, continue
    5. COMMIT changes
    6. Mark story completed
END FOR

RETROSPECTIVE (scrum master)
DOCUMENTATION (tech writer)
CREATE_PR
```

**Prompt Template System:**
- Templates stored as markdown files
- Variable substitution using Python format strings
- Templates for each agent role:
  - `create_story.md`: Epic content, completed stories
  - `add_context.md`: Story content, missing context hints
  - `develop.md`: Story content, previous attempt feedback
  - `code_review.md`: Story content, diff of changes
  - `retrospective.md`: Completed stories, failed stories
  - `documentation.md`: Completed stories, architecture refs

**Error Handling:**
- Phase failures logged and stored in state
- Retryable phases (DEVELOP, CODE_REVIEW) have configurable max attempts
- Non-retryable phase failures mark workflow as failed
- State always persisted before raising exception

### 5.6 TUI Feature

**Location:** `features/tui/`

**Purpose:** Provide terminal-based dashboard for workflow visibility.

**Components:**

| Component | Purpose |
|-----------|---------|
| `BmadAutoApp` | Main Textual application |
| `WorkflowStatusWidget` | Shows current epic, story, phase |
| `StoryTableWidget` | Table of stories with status |
| `AgentLogWidget` | Streaming log of agent output |
| `ControlsWidget` | Pause, skip, quit buttons |
| `HeadlessReporter` | Rich-only output for non-TUI mode |

**TUI Layout:**

```
┌─────────────────────────────────────────────────────────┐
│ bmad-auto                                    12:34:56   │  <- Header
├─────────────────────────────────────────────────────────┤
│ Epic: epic-001.md                                       │
│ Story: STORY-003 - Implement Auth           [3/7] ████░ │  <- Status
│ Phase: DEVELOP (attempt 2/3)                            │
├─────────────────────────────────────────────────────────┤
│ Stories                    │ Agent Log                  │
│ ─────────────────────────  │ ──────────────────────────│
│ ✓ STORY-001  Completed     │ > Reading story file...   │
│ ✓ STORY-002  Completed     │ > Analyzing requirements  │
│ ⟳ STORY-003  In Progress   │ > Generating code...      │  <- Main
│ ○ STORY-004  Pending       │ > Writing tests...        │
│ ○ STORY-005  Pending       │ > Running pytest...       │
├─────────────────────────────────────────────────────────┤
│ [Pause]  [Skip Story]  [Quit]                           │  <- Controls
└─────────────────────────────────────────────────────────┘
```

**Headless Mode:**
- For CI or scripting, TUI is disabled
- Uses Rich for formatted console output
- Progress shown as log lines
- Tables for status summaries

**Keybindings:**
- `q`: Quit application
- `p`: Pause workflow
- `r`: Resume workflow
- `s`: Skip current story
- `?`: Show help

---

## 6. CLI Interface

### 6.1 Installation

```bash
# Run directly without installation (ephemeral)
uvx bmad-auto run --epic docs/epics/epic-001.md

# Install globally for frequent use
uv tool install bmad-auto
bmad-auto run --epic docs/epics/epic-001.md
```

### 6.2 Commands

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `init` | Initialize config in repository | `--repo-path` |
| `run` | Run workflow for epic(s) | `--epic`, `--all`, `--tui`, `--dry-run` |
| `resume` | Resume paused/failed workflow | `--workflow-id` |
| `status` | Show workflow status | `--repo-path` |
| `list` | List discovered epics | `--repo-path` |
| `config validate` | Validate configuration | `--repo-path` |
| `config show` | Display effective configuration | `--repo-path` |

### 6.3 Global Options

| Option | Purpose | Default |
|--------|---------|---------|
| `--repo-path`, `-r` | Target repository path | Current directory |
| `--config`, `-c` | Override config file path | Auto-discover |
| `--verbose`, `-v` | Enable debug logging | False |
| `--quiet`, `-q` | Suppress non-error output | False |

### 6.4 Run Command Options

| Option | Purpose | Default |
|--------|---------|---------|
| `--epic`, `-e` | Specific epic file to process | Required unless `--all` |
| `--all`, `-a` | Process all unprocessed epics | False |
| `--tui`, `-t` | Enable TUI dashboard | False |
| `--headless` | Force headless mode | Auto (True if not TTY) |
| `--dry-run` | Show what would be done | False |
| `--claude-settings` | Override Claude settings file | From config |
| `--codex-config` | Override Codex config file | From config |

---

## 7. Configuration Files

### 7.1 Main Configuration (`.bmad-auto/config.yaml`)

```yaml
version: "1.0"

# Agent configurations by role
scrum_master:
  cli: claude                              # or "codex"
  settings_file: ~/.config/bmad-auto/claude_high.json
  timeout: 600

developer:
  cli: codex
  settings_file: ~/.config/bmad-auto/codex_low.toml
  timeout: 900

reviewer:
  cli: claude
  settings_file: ~/.config/bmad-auto/claude_high.json
  timeout: 300

tech_writer:
  cli: claude
  settings_file: ~/.config/bmad-auto/claude_high.json
  timeout: 600

# Git settings
git:
  auto_branch: true
  branch_prefix: bmad
  commit_prefix: "feat(bmad):"
  auto_push: false
  create_pr: true
  pr_draft: true

# Workflow settings
workflow:
  max_dev_attempts: 3
  pause_between_stories: false
  pause_before_pr: true

# Epic/story discovery
discovery:
  epic_patterns:
    - "docs/epics/*.md"
    - "docs/epics/**/*.md"
  story_output_dir: docs/stories

# State persistence
state_dir: .bmad-auto/state

# Logging
log_level: INFO
log_json: false
```

### 7.2 Claude Code Settings (High Tier)

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write(./src/**)",
      "Write(./tests/**)",
      "Write(./docs/**)",
      "Edit",
      "Bash(npm run *)",
      "Bash(pytest *)",
      "Bash(uv run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Bash(git commit *)",
      "Write(./.env*)"
    ],
    "defaultMode": "acceptEdits"
  },
  "model": "claude-sonnet-4-5-20250514"
}
```

### 7.3 Claude Code Settings (Low Tier)

```json
{
  "permissions": {
    "allow": [
      "Read(./src/**)",
      "Read(./tests/**)",
      "Read(./docs/**)",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Write",
      "Edit",
      "Bash"
    ],
    "defaultMode": "default"
  },
  "model": "claude-haiku-4-5-20251001"
}
```

### 7.4 Codex Config (High Tier)

```toml
model = "o3"
approval_policy = "on-failure"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"
model_reasoning_summary = "detailed"

[history]
persistence = true
```

### 7.5 Codex Config (Low Tier)

```toml
model = "codex-mini"
approval_policy = "never"
sandbox_mode = "workspace-write"
model_reasoning_effort = "low"

[history]
persistence = false
```

---

## 8. Data Models

### 8.1 Agent Models

**AgentConfig:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cli` | `Literal["claude", "codex"]` | Yes | CLI tool to use |
| `settings_file` | `Path \| None` | No | Path to CLI settings file |
| `working_dir` | `Path` | No | Working directory (default: `.`) |
| `timeout` | `int` | No | Timeout in seconds (default: 600) |
| `extra_args` | `list[str]` | No | Additional CLI arguments |

**AgentResult:**
| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether execution succeeded |
| `output` | `str` | Agent's output text |
| `error` | `str \| None` | Error message if failed |
| `session_id` | `str \| None` | Session ID for resume (Claude) |
| `cost_usd` | `float \| None` | API cost if reported |
| `duration_seconds` | `float` | Execution time |

### 8.2 State Models

**WorkflowState:**
| Field | Type | Description |
|-------|------|-------------|
| `workflow_id` | `str` | Unique identifier |
| `epic_file` | `str` | Path to epic file |
| `status` | `str` | pending/running/paused/failed/completed |
| `branch_name` | `str \| None` | Git branch name |
| `branch_created` | `bool` | Whether branch exists |
| `current_phase` | `str` | Current workflow phase |
| `current_story` | `str \| None` | Current story ID |
| `completed_stories` | `list[str]` | List of completed story IDs |
| `failed_stories` | `list[str]` | List of failed story IDs |
| `error` | `str \| None` | Error message if failed |
| `started_at` | `datetime` | When workflow started |
| `updated_at` | `datetime` | Last state update |

### 8.3 Discovery Models

**EpicInfo:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Epic identifier |
| `title` | `str` | Epic title |
| `description` | `str` | Epic description |
| `story_refs` | `list[str]` | Referenced story IDs |
| `dependencies` | `list[str]` | Dependent epic IDs |
| `file_path` | `Path` | Path to epic file |

**StoryInfo:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Story identifier |
| `title` | `str` | Story title |
| `context` | `str` | Full implementation context |
| `acceptance_criteria` | `list[str]` | Acceptance criteria |
| `checklist` | `list[str]` | Implementation checklist |
| `file_path` | `Path` | Path to story file |

---

## 9. Error Handling Strategy

### 9.1 Fail Fast Principle

Per AGENTS.md, the system must:
- Detect invalid state early
- Raise explicit exceptions
- Never use silent fallbacks
- Never swallow errors

### 9.2 Exception Categories

| Category | Recovery | Action |
|----------|----------|--------|
| Configuration errors | None | Fail with clear message |
| Agent not found | None | Fail with installation instructions |
| Agent timeout | Retry | Retry with same config, up to max attempts |
| Agent execution error | Conditional | Retry if retryable phase, else fail |
| Git operation error | None | Fail with git output |
| State persistence error | Retry | Retry once, then fail |

### 9.3 Retry Logic

Retryable phases: `DEVELOP`, `CODE_REVIEW`

Retry configuration:
- Maximum attempts: Configurable (default: 3)
- No exponential backoff (immediate retry)
- Each retry includes previous failure feedback in prompt

### 9.4 Logging on Errors

All errors must be logged with:
- Error type and message
- Relevant context (phase, story, attempt number)
- No sensitive information (API keys, secrets)

---

## 10. Testing Strategy

### 10.1 Coverage Requirements

Per AGENTS.md:
- Minimum 80% code coverage
- Coverage enforced in CI with `--cov-fail-under=80`
- New code must not reduce coverage

### 10.2 Test Organization

Tests are co-located with source code:

```
features/agents/
├── claude.py
├── codex.py
└── tests/
    ├── conftest.py          # Shared fixtures
    ├── test_claude.py       # ClaudeAgent tests
    └── test_codex.py        # CodexAgent tests
```

### 10.3 Test Categories

**Unit Tests:**
- Test individual functions and methods
- Mock all external dependencies
- Fast execution (< 1 second per test)

**Integration Tests:**
- Test component interactions
- Use real file system (temp directories)
- Mock only CLI subprocess calls

**Markers:**
- `@pytest.mark.asyncio` for async tests
- `@pytest.mark.slow` for tests > 5 seconds
- `@pytest.mark.integration` for integration tests

### 10.4 Mocking Strategy

| Dependency | Mock Approach |
|------------|---------------|
| CLI subprocess | Mock `asyncio.create_subprocess_exec` |
| File system | Use `tmp_path` fixture |
| Git repository | Create temp repo with `git init` |
| Time | Mock `datetime.utcnow` |

### 10.5 Fixtures

Common fixtures in `conftest.py`:
- `agent_config`: Default AgentConfig
- `workflow_state`: Default WorkflowState
- `temp_repo`: Temporary git repository
- `mock_claude_success`: Mock successful Claude execution
- `mock_codex_success`: Mock successful Codex execution

---

## 11. Build and Packaging

### 11.1 Build System

Per AGENTS.md, use hatchling:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 11.2 Dependencies

**Runtime:**
- `typer>=0.15.0` - CLI framework
- `rich>=13.9.0` - Terminal formatting
- `textual>=1.0.0` - TUI framework
- `pydantic>=2.10.0` - Data validation
- `pydantic-settings>=2.6.0` - Configuration
- `gitpython>=3.1.0` - Git operations
- `tenacity>=9.0.0` - Retry logic
- `structlog>=24.4.0` - Structured logging
- `pyyaml>=6.0` - YAML parsing

**Development:**
- `pytest>=8.3.0` - Testing
- `pytest-cov>=6.0.0` - Coverage
- `pytest-asyncio>=0.24.0` - Async test support
- `ruff>=0.8.0` - Linting and formatting
- `pyright>=1.1.390` - Type checking

### 11.3 Entry Point

```toml
[project.scripts]
bmad-auto = "bmad_auto.main:main"
```

### 11.4 Package Data

Non-Python files to include:
- `templates/*.yaml`
- `templates/*.json`
- `templates/*.toml`
- `templates/*.md` (prompt templates)

---

## 12. CI/CD Requirements

### 12.1 CI Pipeline Steps

Per AGENTS.md:

1. Install dependencies: `uv sync`
2. Format check: `uv run ruff format --check .`
3. Lint: `uv run ruff check .`
4. Type check: `uv run pyright src/`
5. Test with coverage: `uv run pytest --cov=src --cov-fail-under=80`

### 12.2 Pre-Commit Checklist

Before committing:
- [ ] `uv sync` run and lockfile updated
- [ ] `uv run ruff format .` applied
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright src/` passes
- [ ] `uv run pytest` passes
- [ ] Coverage ≥ 80%
- [ ] No `print` statements
- [ ] No relative imports
- [ ] No magic strings
- [ ] No secrets in code

---

## 13. Repository Files Created in Target

When `bmad-auto init` runs in a target repository:

```
target-repo/
├── .bmad-auto/
│   ├── config.yaml          # Local configuration
│   └── state/               # Workflow state (git-ignored)
│       └── .gitkeep
├── .gitignore               # Updated with .bmad-auto/state/
└── docs/
    └── stories/             # Generated story files
        └── .gitkeep
```

When `bmad-auto run` completes:

```
target-repo/
├── .bmad-auto/
│   └── state/
│       └── epic-001-1734567890.json   # Workflow state
├── docs/
│   └── stories/
│       └── epic-001/
│           ├── story-001.md           # Generated story
│           ├── story-002.md
│           └── story-003.md
└── [implementation files created by agents]
```

---

## 14. Workflow Sequence

### 14.1 Complete Flow Diagram

```
User: uvx bmad-auto run --epic epic-001.md
                │
                ▼
        ┌───────────────┐
        │  Load Config  │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Validate CLI  │──── Not found ──▶ AgentNotFoundError
        │   Tools       │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Create Branch │──── Git error ──▶ GitOperationError
        │  bmad/epic-001│
        └───────┬───────┘
                │
                ▼
    ┌───────────────────────────────────────┐
    │            STORY LOOP                 │
    │  ┌─────────────────────────────────┐  │
    │  │  Create Story (Scrum Master)   │  │
    │  └───────────────┬─────────────────┘  │
    │                  │                    │
    │          "NO_MORE_STORIES"? ─────────────▶ Exit Loop
    │                  │ No                 │
    │                  ▼                    │
    │  ┌─────────────────────────────────┐  │
    │  │     DEVELOPMENT LOOP           │  │
    │  │  ┌───────────────────────────┐ │  │
    │  │  │  Develop (Developer)      │ │  │
    │  │  └─────────────┬─────────────┘ │  │
    │  │                │               │  │
    │  │                ▼               │  │
    │  │  ┌───────────────────────────┐ │  │
    │  │  │  Review (Reviewer)        │ │  │
    │  │  └─────────────┬─────────────┘ │  │
    │  │                │               │  │
    │  │         "APPROVED"? ──────────────▶ Exit Dev Loop
    │  │                │ No            │  │
    │  │                ▼               │  │
    │  │         attempts < max? ──────────▶ Retry with feedback
    │  │                │ No            │  │
    │  │                ▼               │  │
    │  │         Mark Story Failed      │  │
    │  └────────────────────────────────┘  │
    │                  │                    │
    │                  ▼                    │
    │  ┌─────────────────────────────────┐  │
    │  │  Commit Changes (Git)          │  │
    │  └───────────────┬─────────────────┘  │
    │                  │                    │
    │          Continue to next story       │
    └───────────────────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ Retrospective │
        │(Scrum Master) │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Documentation │
        │ (Tech Writer) │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │  Create PR    │
        │   (gh CLI)    │
        └───────┬───────┘
                │
                ▼
            Complete
```

### 14.2 State Transitions

```
pending ──▶ running ──▶ completed
              │
              ├──▶ paused ──▶ running
              │
              └──▶ failed
```

---

## 15. Constants Reference

All magic values defined in `shared/consts.py`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `CLI_CLAUDE` | `"claude"` | Claude CLI command |
| `CLI_CODEX` | `"codex"` | Codex CLI command |
| `DEFAULT_STATE_DIR` | `".bmad-auto/state"` | State storage location |
| `DEFAULT_CONFIG_FILE` | `".bmad-auto/config.yaml"` | Config file name |
| `USER_CONFIG_DIR` | `"~/.config/bmad-auto"` | User-level config |
| `GIT_BRANCH_PREFIX` | `"bmad"` | Git branch prefix |
| `GIT_COMMIT_PREFIX` | `"feat(bmad):"` | Commit message prefix |
| `MAX_DEV_ATTEMPTS` | `3` | Default retry count |
| `DEFAULT_AGENT_TIMEOUT` | `600` | Default timeout (seconds) |
| `MARKER_NO_MORE_STORIES` | `"NO_MORE_STORIES"` | Agent output marker |
| `MARKER_REVIEW_APPROVED` | `"APPROVED"` | Review pass marker |
| `MARKER_REVIEW_REJECTED` | `"REJECTED"` | Review fail marker |
| `DEFAULT_EPIC_PATTERNS` | `("docs/epics/*.md", ...)` | Epic file globs |
| `DEFAULT_STORY_OUTPUT_DIR` | `"docs/stories"` | Generated story location |

---

## 16. Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Project scaffolding with pyproject.toml
- [ ] Constants module (`shared/consts.py`)
- [ ] Exception hierarchy (`core/exceptions.py`)
- [ ] Protocol definitions (`core/protocols.py`)
- [ ] Configuration system (`core/config.py`)
- [ ] Logging setup (`core/logging.py`)
- [ ] Tests for all core modules

### Phase 2: Agent Layer
- [ ] Agent models (`features/agents/models.py`)
- [ ] Base agent implementation (`features/agents/base.py`)
- [ ] Claude agent (`features/agents/claude.py`)
- [ ] Codex agent (`features/agents/codex.py`)
- [ ] Agent factory (`features/agents/factory.py`)
- [ ] Tests with mocked subprocess

### Phase 3: State and Git
- [ ] State models (`features/state/models.py`)
- [ ] State manager (`features/state/manager.py`)
- [ ] Git models (`features/git_ops/models.py`)
- [ ] Git manager (`features/git_ops/manager.py`)
- [ ] Tests with temp directories/repos

### Phase 4: Discovery
- [ ] Epic parser (`features/discovery/epic_parser.py`)
- [ ] Story parser (`features/discovery/story_parser.py`)
- [ ] Tests with sample BMAD files

### Phase 5: Orchestrator
- [ ] Phase definitions (`features/orchestrator/phases.py`)
- [ ] Prompt templates (`features/orchestrator/prompts.py`)
- [ ] Orchestrator engine (`features/orchestrator/engine.py`)
- [ ] Tests with mocked agents

### Phase 6: CLI
- [ ] CLI commands (`cli.py`)
- [ ] Main entry point (`main.py`)
- [ ] Tests for CLI invocations

### Phase 7: TUI
- [ ] Headless reporter (`features/tui/headless.py`)
- [ ] TUI widgets (`features/tui/widgets.py`)
- [ ] TUI application (`features/tui/app.py`)
- [ ] Tests for TUI components

### Phase 8: Polish
- [ ] README.md
- [ ] Template files
- [ ] CI configuration
- [ ] Final coverage check (≥80%)

---

## 17. Summary

This document provides a complete specification for implementing `bmad-auto`, a CLI tool for automating BMAD methodology workflows. The design:

1. **Follows src/AGENTS.md strictly** - Vertical slice architecture, no relative imports, Pydantic models, dependency injection, fail-fast error handling, 80% coverage
2. **Is self-contained** - No external dashboard server, TUI runs in terminal
3. **Is portable** - Installable via uvx, works from any repository
4. **Is resumable** - State persisted to disk, workflows can be paused/resumed
5. **Is extensible** - Protocol-based design allows swapping implementations

The implementation should proceed phase-by-phase, with tests written alongside or before each component.