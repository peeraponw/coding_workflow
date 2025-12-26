---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
status: complete
lastStep: 11
inputDocuments:
  - "project-planning-artifacts/product-brief-bmad-auto-2025-12-25.md"
  - "project-planning-artifacts/research/technical-claude-codex-cli-integration-research-2025-12-25.md"
documentCounts:
  briefs: 1
  research: 1
  brainstorming: 0
  projectDocs: 0
workflowType: 'prd'
lastStep: 0
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-25'
---

# Product Requirements Document - bmad-auto

**Author:** Warm
**Date:** 2025-12-25

## Executive Summary

**bmad-auto** is a uvx-installable CLI tool that automates the implementation phase of the BMAD methodology. It eliminates manual orchestration overhead by providing single-command epic execution with intelligent agent coordination.

**The Core Problem:**
Manual BMAD orchestration requires dozens of CLI invocations per epic—context switching between agents, copying outputs, tracking progress mentally. The cognitive overhead often exceeds the methodology's value.

**The Solution:**
One command. One epic. Reviewed code.

```bash
uvx bmad-auto run --epic docs/epics/epic-001.md
```

The orchestrator manages the story loop: Scrum Master creates stories → Developer implements → Reviewer validates → iterate until approved → auto-commit. State persists to YAML for pause/resume capability.

### What Makes This Special

1. **Hierarchical Model Routing** - Higher-tier models (Claude) judge and control; lower-tier models (GLM) execute implementation. Cost-efficient without sacrificing quality gates.

2. **AFK-Friendly Execution** - Kick off an epic before lunch, return to committed, reviewed code. No babysitting required.

3. **Seamless Pause/Resume** - YAML state persistence means interruptions don't lose progress. Pick up exactly where you left off.

4. **Trust Through Review Gates** - Every commit passes the SM → Dev → Review loop. No silent failures, no corrupted code.

## Project Classification

**Technical Type:** cli_tool
**Domain:** general (developer tooling)
**Complexity:** low
**Project Context:** Greenfield - new project

This is a Python CLI tool distributed via uvx, using the Claude Agent SDK for agent orchestration. No regulated domain concerns; standard developer tooling practices apply.

## Success Criteria

### User Success

bmad-auto succeeds when users experience:

1. **Autonomous Execution** - A story loop completes without manual intervention (SM → Dev → Review → Commit)
2. **Reliable Resume** - Workflow resumes seamlessly after interruption with no lost progress
3. **AFK Capability** - A full epic can be processed while the user is away from keyboard
4. **Trust Threshold** - User reaches for bmad-auto by default instead of manual BMAD orchestration

**The "Worth It" Moment:** Returning from lunch to find committed, reviewed code—without having touched the keyboard.

### Business Success

This is a personal productivity tool. No revenue, growth, or adoption metrics apply.

**Success = "Does it save me time and work reliably?"**

Community adoption (GitHub stars, contributors) is not a success metric.

### Technical Success

1. **State Integrity** - YAML state accurately reflects workflow progress; never corrupted
2. **Clear Error Reporting** - On failure, user knows exactly where it stopped and why
3. **Graceful Degradation** - Technical failures (rate limits, API errors) pause and wait for user intervention rather than corrupting state
4. **Clean Recovery** - User can revert to last working commit if needed

### Measurable Outcomes

| KPI | Target | Measurement |
|-----|--------|-------------|
| Story completion rate | >90% without intervention | Completed / Attempted |
| Resume reliability | 100% successful | Failed resumes / Total attempts |
| Time to first value | <5 minutes | Install to first commit |
| Review loop efficiency | <3 iterations average | Review attempts / Completed stories |

**Failure Handling (the 10%):**
- Workflow pauses, reports failure reason
- State persisted at last successful phase
- User intervenes: retry, revert, or manual fix
- No silent failures or corrupted commits

## Product Scope

### MVP - Minimum Viable Product

**Commands:**
- `bmad-auto run --epic <file>` - Execute story loop for an epic
- `bmad-auto status` - Check current workflow progress
- `bmad-auto resume` - Continue paused/interrupted workflow

**Core Capabilities:**
- Story loop: SM creates story → Dev implements → Reviewer validates → iterate → Commit
- Claude Code only (via Claude Agent SDK)
- Hierarchical model routing (Claude for SM/Reviewer, GLM for Dev via ANTHROPIC_BASE_URL)
- YAML state persistence for pause/resume
- Auto-create feature branch, auto-commit after approved stories
- Headless mode with structured logging

### Growth Features (Post-MVP)

- TUI dashboard for real-time progress visualization
- Codex CLI support for model diversity
- `bmad-auto init` for guided setup
- Auto-PR creation with summary
- Git worktree parallelism for speculative execution

### Vision (Future)

- Tech Writer and Retrospective phases
- Multi-epic parallel processing
- Team collaboration features

## User Journeys

### Journey 1: The Lunchtime Epic (Success Path)

Warm has just finished the planning phase for a new feature in his side project. The epic file is ready: five stories covering a new API endpoint with validation, tests, and documentation. It's 11:45 AM, and his stomach is growling.

Instead of the usual ritual—invoke SM, copy output, invoke Dev, wait, copy output, invoke Reviewer, iterate, commit, repeat—Warm types a single command:

```bash
uvx bmad-auto run --epic docs/epics/epic-001-user-auth.md
```

The terminal shows the orchestrator spinning up. "Story 1 of 5: SM creating story..." He grabs his jacket and heads to lunch.

Forty-five minutes later, Warm returns with a coffee. He glances at the terminal: "Story 4 of 5: Review approved. Committing..." The feature branch has three clean commits already. By the time he's finished his coffee, all five stories are done. He runs `git log --oneline` and sees exactly what he hoped for—five atomic commits, each reviewed and approved.

**The breakthrough moment:** Warm realizes he just shipped a feature while eating pad thai. The cognitive load of BMAD orchestration is gone.

### Journey 2: The 3 AM Rate Limit (Failure/Recovery Path)

Warm kicks off a complex refactoring epic before bed. Six stories, touching core modules. He sets his laptop on the desk and goes to sleep.

At 3 AM, the Claude API hits a rate limit mid-story. The orchestrator detects the failure, persists state to YAML, and logs clearly:

```
[03:14:22] ERROR: Rate limit exceeded (429)
[03:14:22] State saved: story-3, phase: dev, iteration: 2
[03:14:22] Workflow paused. Run 'bmad-auto resume' to continue.
```

Warm wakes up at 7 AM and sees the pause notification. No panic—the state file shows exactly where it stopped. Stories 1 and 2 are committed. Story 3's dev phase was mid-iteration.

He waits an hour for rate limits to reset, then runs `bmad-auto resume`. The orchestrator picks up exactly where it left off. By breakfast, the epic is complete.

**The breakthrough moment:** A failure at 3 AM didn't cost him anything. No corrupted state, no lost work, no guessing. Just resume and continue.

### Journey 3: The Anxious Check-In (Status Monitoring Path)

Warm has a big demo tomorrow. He kicked off an epic an hour ago but keeps wondering: "Is it working? How far along is it?"

Instead of interrupting the workflow, he opens a new terminal and runs `bmad-auto status`:

```
Epic: docs/epics/epic-003-dashboard.md
Status: IN_PROGRESS
Progress: Story 3 of 4

Current Story: "Add chart filtering"
  Phase: review (iteration 1)
  Started: 14:23:07
  Duration: 12m 34s

Completed Stories:
  ✓ Story 1: "Dashboard layout" - committed (abc123)
  ✓ Story 2: "Data fetching" - committed (def456)
```

Warm exhales. Three-quarters done, review phase, no errors. He goes back to his documentation, confident he'll have working code for tomorrow's demo.

**The breakthrough moment:** Visibility without interruption. He knows exactly where things stand without breaking his focus.

### Journey Requirements Summary

| Capability Area | Revealed By |
|-----------------|-------------|
| `run --epic` command | Journey 1 |
| Story loop orchestration (SM → Dev → Review → Commit) | Journey 1 |
| Auto-commit to feature branch | Journey 1 |
| Headless execution with structured logging | Journey 1, 2 |
| Error detection and graceful pause | Journey 2 |
| YAML state persistence | Journey 2 |
| `resume` command with exact state recovery | Journey 2 |
| Clear error messaging | Journey 2 |
| `status` command | Journey 3 |
| Progress reporting (story/phase/iteration) | Journey 3 |
| Non-blocking status checks | Journey 3 |

## CLI Tool Specific Requirements

### Command Structure

**Core Commands (MVP):**

| Command | Purpose | Example |
|---------|---------|---------|
| `bmad-auto run --epic <file>` | Execute story loop for an epic | `bmad-auto run --epic docs/epics/epic-001.md` |
| `bmad-auto status` | Check current workflow progress | `bmad-auto status` |
| `bmad-auto resume` | Continue paused/interrupted workflow | `bmad-auto resume` |

**Command Behavior:**
- All commands are non-interactive (headless)
- No TUI or interactive prompts
- Designed for scriptability and automation

### Output Formats

**Terminal Output (Logs):**
- Plain text, human-readable logs
- Structured workflow progression showing:
  - Current agent (SM, Dev, Reviewer)
  - Current action and status
  - Handoff reasons between agents
  - Next agent in sequence
- Timestamped entries for debugging

**Example Log Output:**
```
[14:23:07] WORKFLOW: Starting epic docs/epics/epic-001.md
[14:23:08] SM: Creating story 1 of 5...
[14:25:12] SM: Story created - "Add user authentication endpoint"
[14:25:12] HANDOFF: SM → Dev (story ready for implementation)
[14:25:13] DEV: Implementing story...
[14:32:45] DEV: Implementation complete (3 files modified)
[14:32:45] HANDOFF: Dev → Reviewer (code ready for review)
[14:32:46] REVIEWER: Reviewing implementation...
```

**Inter-Agent Communication:**
- YAML format for agent handoff files (human-readable, token-efficient)
- State persistence in YAML format (`.bmad-auto-state.yaml`)
- Consistent format across all orchestrator-managed files

### Configuration Schema

**Config File:** `.bmad-auto.yaml` in project root

```yaml
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"

agents:
  sm_model: "claude"               # Uses logged-in Anthropic subscription
  dev_model: "glm"                 # Uses GLM via ANTHROPIC_BASE_URL
  reviewer_model: "claude"         # Uses logged-in Anthropic subscription

git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```

**Environment Variables (GLM only):**
- `ANTHROPIC_API_KEY` - Required only for GLM-routed agents
- `ANTHROPIC_BASE_URL` - Required only for GLM-routed agents

**Authentication:**
- Claude agents: Use logged-in Anthropic subscription (no API key needed)
- GLM agents: Require `ANTHROPIC_API_KEY` + `ANTHROPIC_BASE_URL` environment variables

### Scripting Support

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success - workflow completed |
| 1 | Error - workflow failed (see logs) |
| 2 | Paused - workflow paused, resumable |
| 3 | Config error - invalid configuration |

**Automation-Friendly:**
- No interactive prompts
- Clear exit codes for CI/CD integration
- Structured logging for log aggregation
- `--json` flag for machine-parseable status output (Growth feature)

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP
Solve the core problem (manual BMAD orchestration overhead) with minimal features. No platform plays, no revenue features—just "does this actually work for me?"

**Resource Requirements:** Solo developer

### MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- The Lunchtime Epic (success path) - full autonomous execution
- The 3 AM Rate Limit (failure/recovery) - graceful pause and resume
- The Anxious Check-In (status monitoring) - non-blocking progress visibility

**Must-Have Capabilities:**

| Capability | Rationale |
|------------|-----------|
| `run --epic` command | Core value proposition |
| Story loop orchestration | The entire workflow |
| Hierarchical model routing | Cost optimization |
| YAML state persistence | Pause/resume requirement |
| `status` command | AFK visibility |
| `resume` command | Recovery from interruption |
| Headless logging | Workflow transparency |
| `.bmad-auto.yaml` config | Agent model configuration |
| Auto-branch and auto-commit | Hands-off execution |

**Explicitly Out of MVP:**

| Feature | Reason |
|---------|--------|
| TUI dashboard | Headless logging sufficient |
| Codex CLI support | Simplify integration |
| `init` command | Manual config acceptable |
| Auto-PR creation | `gh pr create` works |
| Shell completion | Convenience, not essential |
| Worktree parallelism | Over-engineering for MVP |

### Post-MVP Features

**Phase 2 (Growth):**
- TUI dashboard for real-time progress visualization
- Codex CLI support for model diversity
- `bmad-auto init` for guided setup
- Auto-PR creation with summary
- Shell completion (bash/zsh/fish)
- `--json` flag for machine-parseable status output

**Phase 3 (Expansion):**
- Git worktree parallelism for speculative execution
- Tech Writer and Retrospective phases
- Multi-epic parallel processing

**Phase 4 (Vision):**
- Team collaboration features

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Mitigation |
|------|------------|
| Claude Agent SDK limitations | Research already done; SDK approach validated |
| Rate limiting during long epics | Graceful pause + resume; user waits and retries |
| State corruption | YAML format human-readable for manual recovery |

**Market Risks:**
Not applicable—personal productivity tool.

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Limited dev time | Tight MVP scope; no scope creep |
| Burnout | AFK-friendly tool means less manual work |

## Functional Requirements

### Workflow Execution

- FR1: User can execute a story loop for an entire epic with a single command
- FR2: User can specify the epic file path as a command argument
- FR3: System can parse BMAD epic files to extract story requirements
- FR4: System can execute stories sequentially until all are complete or a failure occurs

### Agent Orchestration

- FR5: System can invoke Scrum Master agent to create user stories from epic requirements
- FR6: System can invoke Developer agent to implement story requirements
- FR7: System can invoke Reviewer agent to validate implemented code
- FR8: System can iterate the Dev → Review loop until the Reviewer approves
- FR9: System can route SM and Reviewer agents to Claude (logged-in subscription)
- FR10: System can route Developer agent to GLM via ANTHROPIC_BASE_URL
- FR11: System can pass context between agents via YAML handoff files

### State Management

- FR12: System can persist workflow state to YAML file after each phase completion
- FR13: User can resume an interrupted workflow from the exact point of interruption
- FR14: System can detect incomplete workflow state on startup
- FR15: System can recover gracefully from rate limit errors by pausing and persisting state
- FR16: System can recover gracefully from API errors by pausing and persisting state

### Progress Monitoring

- FR17: User can check current workflow status without interrupting execution
- FR18: System can display current agent, action, and phase in progress
- FR19: System can display completed stories with commit references
- FR20: System can log workflow progression with timestamps to terminal
- FR21: System can log handoff events showing source agent, target agent, and reason

### Git Integration

- FR22: System can create a feature branch for the epic automatically
- FR23: System can commit code after each story passes review
- FR24: System can include story reference in commit message
- FR25: User can configure branch naming prefix

### Configuration

- FR26: User can configure agent model assignments in .bmad-auto.yaml
- FR27: System can read GLM credentials from ANTHROPIC_API_KEY environment variable
- FR28: System can read GLM endpoint from ANTHROPIC_BASE_URL environment variable
- FR29: User can configure default epic path in config file
- FR30: User can configure state file location in config file
- FR31: User can configure git auto-branch and auto-commit behavior

### Error Handling

- FR32: System can report clear error messages indicating failure reason and location
- FR33: System can exit with distinct exit codes for success, error, paused, and config error states
- FR34: System can preserve state integrity during unexpected failures

## Non-Functional Requirements

### Reliability

- NFR1: State file must be written atomically to prevent corruption during unexpected termination
- NFR2: Resume operation must restore exact workflow position 100% of the time when state file is intact
- NFR3: System must detect and report corrupted state files rather than proceeding with partial data
- NFR4: Git operations must be atomic—no partial commits that leave repository in inconsistent state
- NFR5: Agent failures must not corrupt previously completed work (committed stories remain committed)

### Integration

- NFR6: System must work with Claude Agent SDK using logged-in Anthropic subscription
- NFR7: System must support GLM routing via standard ANTHROPIC_BASE_URL mechanism
- NFR8: System must parse BMAD epic files in standard markdown format
- NFR9: System must produce YAML files readable by standard YAML parsers
- NFR10: System must integrate with git CLI for branch and commit operations
- NFR11: System must work with standard YAML parsers for configuration

### Security

- NFR12: GLM credentials (ANTHROPIC_API_KEY) must only be read from environment variables, never stored in config files
- NFR13: State files must not contain API credentials or secrets
- NFR14: Log output must not expose API credentials or sensitive request/response content

