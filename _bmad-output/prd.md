---
stepsCompleted: [1, 2, 3, 4, 5, 6]
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

The orchestrator manages the story loop: Scrum Master creates stories → Developer implements → Reviewer validates → iterate until approved → auto-commit. State persists to JSON for pause/resume capability.

### What Makes This Special

1. **Hierarchical Model Routing** - Higher-tier models (Claude) judge and control; lower-tier models (GLM) execute implementation. Cost-efficient without sacrificing quality gates.

2. **AFK-Friendly Execution** - Kick off an epic before lunch, return to committed, reviewed code. No babysitting required.

3. **Seamless Pause/Resume** - JSON state persistence means interruptions don't lose progress. Pick up exactly where you left off.

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

1. **State Integrity** - JSON state accurately reflects workflow progress; never corrupted
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
- JSON state persistence for pause/resume
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

At 3 AM, the Claude API hits a rate limit mid-story. The orchestrator detects the failure, persists state to JSON, and logs clearly:

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
| JSON state persistence | Journey 2 |
| `resume` command with exact state recovery | Journey 2 |
| Clear error messaging | Journey 2 |
| `status` command | Journey 3 |
| Progress reporting (story/phase/iteration) | Journey 3 |
| Non-blocking status checks | Journey 3 |

