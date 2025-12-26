---
stepsCompleted: [1]
inputDocuments:
  - "_bmad-output/prd.md"
  - "_bmad-output/architecture.md"
workflowType: 'epics'
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-26'
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

{{requirements_coverage_map}}

## Epic List

{{epics_list}}
