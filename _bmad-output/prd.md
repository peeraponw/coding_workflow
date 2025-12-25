---
stepsCompleted: [1, 2, 3]
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

