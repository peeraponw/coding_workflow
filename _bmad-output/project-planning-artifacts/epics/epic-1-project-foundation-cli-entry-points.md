# Epic 1: Project Foundation & CLI Entry Points

User can install bmad-auto and invoke basic commands with proper configuration loading.

**FRs covered:** FR1, FR2, FR26-31, FR32-33

## Story 1.1: Shared Module Setup

As a **developer**,
I want **a shared module with constants, types, and exceptions**,
So that **all other modules have consistent definitions to import from**.

**Acceptance Criteria:**

**Given** the project is initialized
**When** I import from `bmad_auto.shared`
**Then** I can access:
- `consts.py` with EXIT_SUCCESS (0), EXIT_ERROR (1), EXIT_PAUSED (2), EXIT_CONFIG_ERROR (3)
- `consts.py` with AGENT_SM, AGENT_DEV, AGENT_REVIEWER
- `consts.py` with PHASE_SM, PHASE_DEV, PHASE_REVIEW
- `consts.py` with STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_PAUSED, STATUS_COMPLETED, STATUS_FAILED
- `types.py` with type aliases for common patterns
- `exceptions.py` with BmadAutoError, ConfigError, StateCorruptionError, AgentError, WorkflowPausedError

**And** all modules pass pyright type checking
**And** ruff linting passes with no errors

---

## Story 1.2: Logging Infrastructure

As a **developer**,
I want **structured logging with structlog and Rich console output**,
So that **logs are machine-parseable and user output is readable**.

**Acceptance Criteria:**

**Given** the shared module exists
**When** I import logging utilities from `bmad_auto.shared.logging`
**Then** I can:
- Get a structlog logger with `get_logger(__name__)`
- Access a Rich Console instance for user-facing output
- Log with context: `logger.info("message", key=value)`

**And** log output includes timestamps
**And** Rich console supports color-coded agent phases (SM=blue, Dev=green, Reviewer=yellow)
**And** tests verify logging configuration works correctly

---

## Story 1.3: Configuration Loading

As a **user**,
I want **to configure bmad-auto via `.bmad-auto.yaml` and environment variables**,
So that **I can customize agent models, paths, and git behavior**.

**Acceptance Criteria:**

**Given** I have a `.bmad-auto.yaml` file in my project root:
```yaml
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "claude"
  dev_model: "glm"
  reviewer_model: "claude"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```
**When** I run any bmad-auto command
**Then** the configuration is loaded and validated

**Given** I set `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` environment variables
**When** configuration is loaded
**Then** GLM credentials are available for agent routing (FR27, FR28)
**And** credentials are NOT stored in any config or state files (NFR12)

**Given** `.bmad-auto.yaml` is missing or invalid
**When** I run a bmad-auto command
**Then** I get a clear ConfigError with exit code 3 (EXIT_CONFIG_ERROR)

**And** internal defaults (timeouts, retries) come from pydantic_settings
**And** tests cover valid config, missing config, and invalid config scenarios

---

## Story 1.4: CLI Entry Point with Commands

As a **user**,
I want **to invoke bmad-auto commands from my terminal**,
So that **I can start workflows, check status, and resume paused work**.

**Acceptance Criteria:**

**Given** bmad-auto is installed via `uvx bmad-auto`
**When** I run `bmad-auto --help`
**Then** I see available commands: `run`, `status`, `resume`

**Given** the CLI is invoked
**When** I run `bmad-auto run --epic docs/epics/epic-001.md`
**Then** the command accepts the epic path argument (FR1, FR2)
**And** returns a stub message (actual orchestration in Epic 3)

**Given** the CLI is invoked
**When** I run `bmad-auto status`
**Then** the command executes (stub for now, full implementation in Epic 4)

**Given** the CLI is invoked
**When** I run `bmad-auto resume`
**Then** the command executes (stub for now, full implementation in Epic 2)

**Given** any command fails
**When** an error occurs
**Then** the CLI exits with appropriate exit code (FR33):
- 0 = success
- 1 = error
- 2 = paused
- 3 = config error

**And** pyproject.toml has `[project.scripts]` entry for `bmad-auto`
**And** `uvx bmad-auto` works after installation

---
