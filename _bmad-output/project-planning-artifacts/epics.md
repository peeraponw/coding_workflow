---
stepsCompleted: [1, 2, 3, 4]
status: complete
inputDocuments:
  - "_bmad-output/prd.md"
  - "_bmad-output/architecture.md"
workflowType: 'epics'
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-26'
completedAt: '2025-12-26'
epicCount: 5
storyCount: 23
frCoverage: 34
---

# bmad-auto - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for bmad-auto, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

**Workflow Execution:**
- FR1: User can execute a story loop for an entire epic with a single command
- FR2: User can specify the epic file path as a command argument
- FR3: System can parse BMAD epic files to extract story requirements
- FR4: System can execute stories sequentially until all are complete or a failure occurs

**Agent Orchestration:**
- FR5: System can invoke Scrum Master agent to create user stories from epic requirements
- FR6: System can invoke Developer agent to implement story requirements
- FR7: System can invoke Reviewer agent to validate implemented code
- FR8: System can iterate the Dev → Review loop until the Reviewer approves
- FR9: System can route SM and Reviewer agents to Claude (logged-in subscription)
- FR10: System can route Developer agent to GLM via ANTHROPIC_BASE_URL
- FR11: System can pass context between agents via YAML handoff files

**State Management:**
- FR12: System can persist workflow state to YAML file after each phase completion
- FR13: User can resume an interrupted workflow from the exact point of interruption
- FR14: System can detect incomplete workflow state on startup
- FR15: System can recover gracefully from rate limit errors by pausing and persisting state
- FR16: System can recover gracefully from API errors by pausing and persisting state

**Progress Monitoring:**
- FR17: User can check current workflow status without interrupting execution
- FR18: System can display current agent, action, and phase in progress
- FR19: System can display completed stories with commit references
- FR20: System can log workflow progression with timestamps to terminal
- FR21: System can log handoff events showing source agent, target agent, and reason

**Git Integration:**
- FR22: System can create a feature branch for the epic automatically
- FR23: System can commit code after each story passes review
- FR24: System can include story reference in commit message
- FR25: User can configure branch naming prefix

**Configuration:**
- FR26: User can configure agent model assignments in .bmad-auto.yaml
- FR27: System can read GLM credentials from ANTHROPIC_API_KEY environment variable
- FR28: System can read GLM endpoint from ANTHROPIC_BASE_URL environment variable
- FR29: User can configure default epic path in config file
- FR30: User can configure state file location in config file
- FR31: User can configure git auto-branch and auto-commit behavior

**Error Handling:**
- FR32: System can report clear error messages indicating failure reason and location
- FR33: System can exit with distinct exit codes for success, error, paused, and config error states
- FR34: System can preserve state integrity during unexpected failures

### NonFunctional Requirements

**Reliability:**
- NFR1: State file must be written atomically to prevent corruption during unexpected termination
- NFR2: Resume operation must restore exact workflow position 100% of the time when state file is intact
- NFR3: System must detect and report corrupted state files rather than proceeding with partial data
- NFR4: Git operations must be atomic—no partial commits that leave repository in inconsistent state
- NFR5: Agent failures must not corrupt previously completed work (committed stories remain committed)

**Integration:**
- NFR6: System must work with Claude Agent SDK using logged-in Anthropic subscription
- NFR7: System must support GLM routing via standard ANTHROPIC_BASE_URL mechanism
- NFR8: System must parse BMAD epic files in standard markdown format
- NFR9: System must produce YAML files readable by standard YAML parsers
- NFR10: System must integrate with git CLI for branch and commit operations
- NFR11: System must work with standard YAML parsers for configuration

**Security:**
- NFR12: GLM credentials (ANTHROPIC_API_KEY) must only be read from environment variables, never stored in config files
- NFR13: State files must not contain API credentials or secrets
- NFR14: Log output must not expose API credentials or sensitive request/response content

### Additional Requirements

**From Architecture - Starter Template:**
- Project initialization: `uv init --package --build-backend hatchling bmad-auto`
- Dependencies: typer[all], pyyaml, claude-agent-sdk, anyio, structlog, pydantic-settings
- Dev dependencies: pytest, pytest-asyncio, pytest-cov, ruff, pyright
- Epic 1 Story 1 must initialize the project using this command

**From Architecture - Agent Invocation Pattern:**
- bmad-auto invokes existing bmad agents via skill commands (e.g., `/bmad:bmm:agents:sm`)
- bmad-auto does NOT build prompts directly—it orchestrates agent invocations
- `agents/prompts.py` renamed to `agents/commands.py` (builds command strings)

**From Architecture - Configuration Layers:**
- Internal defaults via pydantic_settings (timeouts, retries)
- User config via `.bmad-auto.yaml` (epic path, models, git settings)
- Secrets via `.env` (ANTHROPIC_API_KEY, ANTHROPIC_BASE_URL)

**From Architecture - Project Structure:**
- Vertical slice architecture per AGENTS.md
- Tests co-located with features in `tests/` subdirectories
- All constants in `shared/consts.py`
- structlog for logging, Rich for display
- 80% minimum test coverage

**From Architecture - Code Standards:**
- Files: ≤500 lines
- Functions: ≤50 lines
- Classes: ≤100 lines
- Line length: 100 characters
- Semantic commit messages

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | Execute story loop with single command |
| FR2 | Epic 1 | Specify epic file path as argument |
| FR3 | Epic 2 | Parse BMAD epic files |
| FR4 | Epic 2 | Execute stories sequentially |
| FR5 | Epic 3 | Invoke SM agent |
| FR6 | Epic 3 | Invoke Dev agent |
| FR7 | Epic 3 | Invoke Reviewer agent |
| FR8 | Epic 3 | Iterate Dev → Review loop |
| FR9 | Epic 3 | Route SM/Reviewer to Claude |
| FR10 | Epic 3 | Route Dev to GLM |
| FR11 | Epic 3 | Pass context via YAML handoff |
| FR12 | Epic 2 | Persist state to YAML |
| FR13 | Epic 2 | Resume from exact point |
| FR14 | Epic 2 | Detect incomplete state |
| FR15 | Epic 2 | Recover from rate limits |
| FR16 | Epic 2 | Recover from API errors |
| FR17 | Epic 4 | Check status without interrupting |
| FR18 | Epic 4 | Display current agent/action/phase |
| FR19 | Epic 4 | Display completed stories with commits |
| FR20 | Epic 4 | Log progression with timestamps |
| FR21 | Epic 4 | Log handoff events |
| FR22 | Epic 5 | Create feature branch |
| FR23 | Epic 5 | Commit after review approval |
| FR24 | Epic 5 | Include story reference in commit |
| FR25 | Epic 5 | Configure branch prefix |
| FR26 | Epic 1 | Configure agent model assignments |
| FR27 | Epic 1 | Read GLM credentials from env |
| FR28 | Epic 1 | Read GLM endpoint from env |
| FR29 | Epic 1 | Configure default epic path |
| FR30 | Epic 1 | Configure state file location |
| FR31 | Epic 1 | Configure git auto-branch/commit |
| FR32 | Epic 1 | Clear error messages |
| FR33 | Epic 1 | Distinct exit codes |
| FR34 | Epic 2 | Preserve state during failures |

## Epic List

### Epic 1: Project Foundation & CLI Entry Points
User can install bmad-auto and invoke basic commands with proper configuration loading.

**FRs covered:** FR1, FR2, FR26-31, FR32-33

**Scope:**
- CLI commands: `run --epic`, `status`, `resume` (entry points only)
- Config loading (`.bmad-auto.yaml` + env vars)
- Exit codes for scripting
- Basic error reporting structure
- Shared module (consts, exceptions, types, logging)

**Note:** Project initialization already complete.

---

### Epic 2: State Persistence & Resume Capability
User can pause/interrupt a workflow and resume exactly where they left off.

**FRs covered:** FR3, FR4, FR12-16, FR34

**Scope:**
- Epic file parsing
- YAML state persistence (atomic writes)
- Resume from exact interruption point
- Graceful error recovery (rate limits, API errors)
- State integrity preservation

---

### Epic 3: Agent Orchestration & Story Loop
User can execute the full SM → Dev → Review → Commit loop automatically.

**FRs covered:** FR5-11

**Scope:**
- Agent invocation via bmad skill commands
- SM agent: creates stories from epic
- Dev agent: implements stories
- Reviewer agent: validates code
- Dev → Review iteration until approval
- Model routing (Claude for SM/Reviewer, GLM for Dev)
- YAML handoff files between agents

---

### Epic 4: Progress Monitoring & Logging
User can check workflow status without interrupting execution.

**FRs covered:** FR17-21

**Scope:**
- `status` command shows current progress
- Timestamped terminal logging
- Agent handoff visibility (from → to → reason)
- Completed stories with commit references
- Non-blocking status checks

---

### Epic 5: Git Integration & Auto-Commit
User returns to find committed, reviewed code on a feature branch.

**FRs covered:** FR22-25

**Scope:**
- Auto-create feature branch for epic
- Auto-commit after each story passes review
- Story reference in commit messages
- Configurable branch naming prefix

---

## Epic 1: Project Foundation & CLI Entry Points

User can install bmad-auto and invoke basic commands with proper configuration loading.

**FRs covered:** FR1, FR2, FR26-31, FR32-33

### Story 1.1: Shared Module Setup

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

### Story 1.2: Logging Infrastructure

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

### Story 1.3: Configuration Loading

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

### Story 1.4: CLI Entry Point with Commands

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

## Epic 2: State Persistence & Resume Capability

User can pause/interrupt a workflow and resume exactly where they left off.

**FRs covered:** FR3, FR4, FR12-16, FR34

### Story 2.1: Epic File Parser

As a **user**,
I want **bmad-auto to parse my epic markdown files**,
So that **stories can be extracted and executed sequentially**.

**Acceptance Criteria:**

**Given** an epic file in standard BMAD markdown format:
```markdown
# Epic: User Authentication
## Story 1: User Registration
...acceptance criteria...
## Story 2: User Login
...acceptance criteria...
```
**When** I run `bmad-auto run --epic path/to/epic.md`
**Then** the parser extracts:
- Epic title and description
- List of stories with their content
- Story count for progress tracking

**Given** an epic file with invalid format
**When** parsing is attempted
**Then** a clear error message identifies the parsing issue

**And** parser handles edge cases (empty stories, missing sections)
**And** tests cover valid epics, malformed epics, and edge cases (FR3)

---

### Story 2.2: Workflow State Model

As a **developer**,
I want **a comprehensive WorkflowState dataclass**,
So that **all workflow progress can be tracked and persisted**.

**Acceptance Criteria:**

**Given** the state module is implemented
**When** I create a WorkflowState instance
**Then** it includes:
- `workflow.epic_path`: path to the epic file
- `workflow.status`: pending | in_progress | paused | completed | failed
- `workflow.branch`: git branch name
- `stories.total`: total story count
- `stories.current_index`: 0-based index of current story
- `stories.completed`: list of {story_id, commit_hash}
- `current_story.id`: current story identifier
- `current_story.phase`: sm | dev | review
- `current_story.iteration`: review iteration count
- `current_story.started_at`: ISO timestamp
- `error.type`: error classification (if any)
- `error.message`: error details (if any)
- `error.phase`: phase where error occurred

**And** state model matches the YAML format from Architecture doc
**And** all fields have appropriate type hints
**And** tests verify state model creation and validation

---

### Story 2.3: State Persistence with Atomic Writes

As a **user**,
I want **workflow state saved atomically after each phase**,
So that **unexpected termination never corrupts my progress**.

**Acceptance Criteria:**

**Given** a workflow is in progress
**When** a phase completes (SM done, Dev done, Review done)
**Then** state is persisted to `.bmad-auto-state.yaml` (FR12)

**Given** state needs to be written
**When** the write operation executes
**Then** it uses atomic write (write to temp, then rename) (NFR1)
**And** partial writes never leave corrupted state files

**Given** a state file exists
**When** state is loaded
**Then** the WorkflowState is reconstructed accurately
**And** integrity is validated (NFR3)

**Given** a corrupted state file
**When** loading is attempted
**Then** StateCorruptionError is raised with clear message
**And** user is informed how to recover

**And** tests verify atomic write behavior
**And** tests verify corruption detection

---

### Story 2.4: Resume Detection & Recovery

As a **user**,
I want **to resume an interrupted workflow from the exact point**,
So that **I don't lose progress when things go wrong**.

**Acceptance Criteria:**

**Given** a state file exists with `status: in_progress` or `status: paused`
**When** I run `bmad-auto resume`
**Then** the workflow resumes from `current_story` at `current_story.phase` (FR13)

**Given** a state file exists with `status: in_progress`
**When** I run `bmad-auto run --epic <same-epic>`
**Then** I'm warned about existing in-progress workflow
**And** prompted to use `resume` instead (FR14)

**Given** a state file exists with `status: completed`
**When** I run `bmad-auto resume`
**Then** I'm informed the workflow is already complete

**Given** no state file exists
**When** I run `bmad-auto resume`
**Then** I get a clear error: "No workflow to resume"

**And** resume restores exact position 100% of the time (NFR2)
**And** tests cover all resume scenarios

---

### Story 2.5: Graceful Error Recovery

As a **user**,
I want **the workflow to pause gracefully on errors**,
So that **I can retry after fixing the issue without losing work**.

**Acceptance Criteria:**

**Given** a workflow is executing
**When** a rate limit error (429) occurs
**Then** state is saved with `status: paused` and `error.type: rate_limit` (FR15)
**And** workflow exits with code 2 (EXIT_PAUSED)
**And** log message: "Rate limit exceeded. Run 'bmad-auto resume' to continue."

**Given** a workflow is executing
**When** an API error occurs (500, timeout, network)
**Then** state is saved with `status: paused` and `error.type: api_error` (FR16)
**And** workflow exits with code 2 (EXIT_PAUSED)
**And** log message includes error details and resume instruction

**Given** an unexpected error occurs
**When** the error handler catches it
**Then** state integrity is preserved (FR34)
**And** previously completed stories remain committed (NFR5)
**And** current phase progress is saved

**And** tests verify graceful pause for each error type
**And** tests verify state integrity after errors

---

## Epic 3: Agent Orchestration & Story Loop

User can execute the full SM → Dev → Review → Commit loop automatically.

**FRs covered:** FR5-11

### Story 3.1: Agent Protocol & Base Implementation

As a **developer**,
I want **a clear AgentProtocol interface and result types**,
So that **all agents have consistent invocation patterns**.

**Acceptance Criteria:**

**Given** the agents module is implemented
**When** I import from `bmad_auto.agents.base`
**Then** I can access:
- `AgentProtocol` with async `run(command: str) -> AgentResult` method
- `AgentResult` dataclass with: success (bool), output (str), error (Optional[str])
- `AgentRole` enum: SM, DEV, REVIEWER

**And** AgentProtocol is a Python Protocol (structural typing)
**And** tests verify protocol compliance
**And** type hints are complete for pyright

---

### Story 3.2: Claude Agent Adapter

As a **developer**,
I want **a Claude Agent SDK wrapper implementing AgentProtocol**,
So that **I can invoke Claude-based agents uniformly**.

**Acceptance Criteria:**

**Given** Claude Agent SDK is available
**When** I create a ClaudeAgent instance
**Then** it implements AgentProtocol

**Given** a ClaudeAgent instance
**When** I call `await agent.run("/bmad:bmm:agents:sm create story")`
**Then** the command is executed via Claude Agent SDK (FR5, FR6, FR7)
**And** AgentResult is returned with output or error

**Given** the agent execution fails
**When** an API error occurs
**Then** AgentResult.success is False
**And** AgentResult.error contains the error message

**And** adapter uses anyio for async compatibility (NFR6)
**And** tests use mocked SDK responses
**And** integration tests verify real agent invocation

---

### Story 3.3: Agent Command Builder

As a **developer**,
I want **command builders for SM, Dev, and Reviewer agents**,
So that **the orchestrator can construct correct skill commands**.

**Acceptance Criteria:**

**Given** I need to invoke the SM agent
**When** I call `build_sm_command(epic_content, story_index)`
**Then** I get a command string like:
```
/bmad:bmm:agents:sm create story {story_index} from epic
```

**Given** I need to invoke the Dev agent
**When** I call `build_dev_command(story_content)`
**Then** I get a command string like:
```
/bmad:bmm:agents:dev implement story
```

**Given** I need to invoke the Reviewer agent
**When** I call `build_reviewer_command(story_content, implementation_diff)`
**Then** I get a command string like:
```
/bmad:bmm:workflows:code-review review implementation
```

**And** commands include necessary context references
**And** tests verify command format for each agent role

---

### Story 3.4: Model Routing Configuration

As a **user**,
I want **SM and Reviewer to use Claude, and Dev to use GLM**,
So that **I get quality gates from Claude while saving costs on implementation**.

**Acceptance Criteria:**

**Given** config specifies:
```yaml
agents:
  sm_model: "claude"
  dev_model: "glm"
  reviewer_model: "claude"
```
**When** the orchestrator creates agents
**Then** SM agent uses logged-in Claude subscription (FR9)
**And** Dev agent uses GLM via ANTHROPIC_BASE_URL (FR10)
**And** Reviewer agent uses logged-in Claude subscription (FR9)

**Given** GLM is configured for Dev
**When** Dev agent is created
**Then** it uses ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL from environment (FR27, FR28)

**Given** model config is invalid
**When** agent creation is attempted
**Then** ConfigError is raised with clear message

**And** tests verify routing for each model configuration
**And** credentials are never logged (NFR14)

---

### Story 3.5: Story Loop Orchestrator

As a **user**,
I want **the full SM → Dev → Review loop to run automatically**,
So that **stories are implemented and validated without manual intervention**.

**Acceptance Criteria:**

**Given** an epic with stories is parsed
**When** I run `bmad-auto run --epic path/to/epic.md`
**Then** for each story:
1. SM agent creates/refines the story (FR5)
2. Dev agent implements the story (FR6)
3. Reviewer agent validates the implementation (FR7)
4. If review fails, loop back to Dev with feedback (FR8)
5. If review passes, mark story complete

**Given** a review iteration
**When** the Reviewer rejects the implementation
**Then** Dev receives the feedback and implements fixes
**And** the loop continues until approval or max iterations

**Given** max review iterations (3) is reached
**When** the Reviewer still rejects
**Then** workflow pauses with `status: paused` and `error.type: review_failed`
**And** user can intervene and resume

**And** state is saved after each phase transition (FR12)
**And** tests verify the complete loop with mocked agents

---

### Story 3.6: Context Passing via YAML Handoff

As a **developer**,
I want **context passed between agents via YAML handoff files**,
So that **each agent has the information it needs without prompt pollution**.

**Acceptance Criteria:**

**Given** SM agent completes
**When** handoff to Dev occurs
**Then** a YAML file is created with:
- Story content from SM
- Acceptance criteria
- Any relevant context

**Given** Dev agent completes
**When** handoff to Reviewer occurs
**Then** a YAML file is created with:
- Original story content
- Implementation summary
- Files changed
- Git diff reference

**Given** Reviewer provides feedback
**When** handoff back to Dev occurs
**Then** a YAML file is created with:
- Review feedback
- Specific issues to address
- Previous iteration context

**And** handoff files are stored in `.bmad-auto/handoffs/` directory (FR11)
**And** handoff files are human-readable for debugging
**And** tests verify handoff file creation and content

---

## Epic 4: Progress Monitoring & Logging

User can check workflow status without interrupting execution.

**FRs covered:** FR17-21

### Story 4.1: Status Command Implementation

As a **user**,
I want **to check workflow status without interrupting execution**,
So that **I can monitor progress while AFK**.

**Acceptance Criteria:**

**Given** a workflow is in progress
**When** I run `bmad-auto status` in another terminal
**Then** I see: (FR17)
```
Epic: docs/epics/epic-001.md
Status: IN_PROGRESS
Progress: Story 3 of 5

Current Story: "Add user validation"
  Phase: review (iteration 2)
  Started: 14:23:07
  Duration: 12m 34s

Completed Stories:
  ✓ Story 1: "Setup project" - committed (abc123)
  ✓ Story 2: "Add models" - committed (def456)
```

**Given** no workflow is in progress
**When** I run `bmad-auto status`
**Then** I see: "No active workflow. Run 'bmad-auto run --epic <file>' to start."

**Given** workflow is paused due to error
**When** I run `bmad-auto status`
**Then** I see status: PAUSED with error details and resume instructions

**And** status command reads state file without locking (non-blocking)
**And** tests verify all status display scenarios

---

### Story 4.2: Timestamped Workflow Logging

As a **user**,
I want **timestamped logs showing workflow progression**,
So that **I can see what's happening and debug issues**.

**Acceptance Criteria:**

**Given** a workflow is executing
**When** any workflow event occurs
**Then** it's logged with ISO timestamp: (FR20)
```
[2025-12-26T14:23:07] WORKFLOW: Starting epic docs/epics/epic-001.md
[2025-12-26T14:23:08] SM: Creating story 1 of 5...
[2025-12-26T14:25:12] SM: Story created - "Add user authentication"
[2025-12-26T14:25:13] DEV: Implementing story...
[2025-12-26T14:32:45] DEV: Implementation complete (3 files modified)
[2025-12-26T14:32:46] REVIEWER: Reviewing implementation...
```

**Given** an error occurs
**When** the error is logged
**Then** timestamp and error details are included
**And** no credentials or sensitive data appear in logs (NFR14)

**And** logs use Rich formatting with colors
**And** agent phases are color-coded (SM=blue, Dev=green, Reviewer=yellow)
**And** tests verify log format and timestamp presence

---

### Story 4.3: Agent Handoff Logging

As a **user**,
I want **to see when agents hand off to each other**,
So that **I understand the workflow progression**.

**Acceptance Criteria:**

**Given** SM completes and hands off to Dev
**When** the handoff occurs
**Then** log shows: (FR21)
```
[14:25:12] HANDOFF: SM → Dev (story ready for implementation)
```

**Given** Dev completes and hands off to Reviewer
**When** the handoff occurs
**Then** log shows:
```
[14:32:45] HANDOFF: Dev → Reviewer (code ready for review)
```

**Given** Reviewer rejects and hands back to Dev
**When** the handoff occurs
**Then** log shows:
```
[14:35:22] HANDOFF: Reviewer → Dev (revision needed: missing error handling)
```

**Given** Reviewer approves
**When** the approval occurs
**Then** log shows:
```
[14:38:15] REVIEW: Approved - proceeding to commit
```

**And** handoff reasons are concise but informative
**And** tests verify handoff log format

---

### Story 4.4: Progress Display with Commit References

As a **user**,
I want **to see completed stories with their commit hashes**,
So that **I can verify what's been done and review commits**.

**Acceptance Criteria:**

**Given** stories have been completed and committed
**When** I view status or logs
**Then** I see commit references: (FR18, FR19)
```
Completed Stories:
  ✓ Story 1: "Setup project structure" - committed (a1b2c3d)
  ✓ Story 2: "Add user model" - committed (e4f5g6h)
  ✓ Story 3: "Implement registration" - committed (i7j8k9l)
```

**Given** a story is in progress
**When** I view status
**Then** I see current phase and iteration:
```
Current Story: "Add login endpoint"
  Phase: dev
  Iteration: 1
  Started: 14:45:22
```

**Given** workflow completes successfully
**When** I view final status
**Then** I see summary:
```
Epic: docs/epics/epic-001.md
Status: COMPLETED
Total Stories: 5
Total Commits: 5
Branch: epic/epic-001
Duration: 45m 12s
```

**And** commit hashes are clickable/copyable short format (7 chars)
**And** tests verify progress display formatting

---

## Epic 5: Git Integration & Auto-Commit

User returns to find committed, reviewed code on a feature branch.

**FRs covered:** FR22-25

### Story 5.1: Git Handler Module

As a **developer**,
I want **a git handler module that wraps git CLI operations**,
So that **all git operations are centralized and testable**.

**Acceptance Criteria:**

**Given** the git_integration module is implemented
**When** I import from `bmad_auto.features.git_integration`
**Then** I can access GitHandler with methods:
- `get_current_branch() -> str`
- `create_branch(name: str) -> bool`
- `checkout_branch(name: str) -> bool`
- `commit(message: str) -> str` (returns commit hash)
- `get_status() -> GitStatus`
- `get_diff() -> str`

**Given** a git operation fails
**When** the subprocess returns non-zero
**Then** appropriate exception is raised with git error message

**And** all operations use subprocess with git CLI (NFR10)
**And** operations are atomic where possible (NFR4)
**And** tests use a temporary git repository fixture

---

### Story 5.2: Feature Branch Creation

As a **user**,
I want **a feature branch created automatically when I start an epic**,
So that **my work is isolated from main branch**.

**Acceptance Criteria:**

**Given** I run `bmad-auto run --epic docs/epics/epic-001.md`
**When** the workflow starts
**Then** a feature branch is created: `epic/epic-001` (FR22)
**And** the branch is checked out
**And** state records `workflow.branch: epic/epic-001`

**Given** config has `git.auto_branch: true`
**When** workflow starts
**Then** branch is created automatically

**Given** config has `git.auto_branch: false`
**When** workflow starts
**Then** no branch is created (user manages branches)

**Given** the target branch already exists
**When** workflow starts
**Then** user is warned and asked to confirm using existing branch

**And** branch name is derived from epic filename
**And** tests verify branch creation scenarios

---

### Story 5.3: Auto-Commit After Review Approval

As a **user**,
I want **code committed automatically after review approval**,
So that **I return to find clean, atomic commits**.

**Acceptance Criteria:**

**Given** Reviewer approves a story implementation
**When** the approval is processed
**Then** all changes are committed with message: (FR23, FR24)
```
feat(epic-001): Story 1 - Add user authentication

Implements user registration and login endpoints.

Story: epic-001/story-1
Reviewed-by: bmad-auto
```

**Given** config has `git.auto_commit: true`
**When** review passes
**Then** commit is created automatically

**Given** config has `git.auto_commit: false`
**When** review passes
**Then** changes are staged but not committed (user commits manually)

**Given** there are no changes to commit
**When** commit is attempted
**Then** workflow logs warning and continues (idempotent)

**And** commit hash is stored in state: `stories.completed[].commit`
**And** commits are atomic - all or nothing (NFR4)
**And** tests verify commit creation and message format

---

### Story 5.4: Branch Naming Configuration

As a **user**,
I want **to configure the branch naming prefix**,
So that **branches match my team's conventions**.

**Acceptance Criteria:**

**Given** config specifies:
```yaml
git:
  branch_prefix: "feature/"
```
**When** workflow starts for `epic-001.md`
**Then** branch is named `feature/epic-001` (FR25)

**Given** config specifies:
```yaml
git:
  branch_prefix: "epic/"
```
**When** workflow starts
**Then** branch is named `epic/epic-001` (default)

**Given** config specifies empty prefix:
```yaml
git:
  branch_prefix: ""
```
**When** workflow starts
**Then** branch is named `epic-001` (no prefix)

**And** branch names are sanitized (no spaces, special chars)
**And** tests verify branch naming with various prefixes
