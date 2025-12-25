---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: complete
inputDocuments:
  - "_bmad-output/project-planning-artifacts/research/technical-claude-codex-cli-integration-research-2025-12-25.md"
  - "docs/description.md"
workflowType: 'product-brief'
lastStep: 0
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-25'
---

# Product Brief: bmad-auto

## Executive Summary

**bmad-auto** is a uvx-installable CLI tool that automates the implementation phase of the BMAD methodology. It eliminates the manual orchestration overhead of invoking AI coding agents, managing context between roles, and tracking story progress.

**One command. One epic. Reviewed code.**

```bash
uvx bmad-auto run --epic docs/epics/epic-001.md
```

The tool orchestrates a story-driven development loop: Scrum Master creates stories, Developer implements them, Reviewer validates the code—iterating until approval, then committing the result. State is persisted for pause/resume capability.

**Target User:** Solo developers using BMAD methodology (open-source for community adoption).

---

## Core Vision

### Problem Statement

The BMAD methodology defines a structured workflow with specialized agent roles (Scrum Master, Developer, Reviewer). Currently, executing this workflow requires painful manual orchestration:

1. **Context switching** - Constantly jumping between CLI invocations and copying output from one agent to the next
2. **Repetitive prompts** - Typing similar role-specific instructions repeatedly
3. **Role friction** - Each BMAD role has its own command/prompt, adding overhead when switching tasks
4. **Lost progress** - Forgetting where you left off or which stories are complete
5. **No visibility** - No unified view of workflow state across the epic

### Problem Impact

These friction points compound exponentially. A single epic with 5 stories requires dozens of manual CLI invocations, context copies, and mental bookkeeping. The cognitive overhead often exceeds the value of the structured methodology itself.

### Why Existing Solutions Fall Short

- **Raw CLI tools (Claude Code, Codex):** Excellent for single-agent tasks, but no built-in multi-agent orchestration or workflow state
- **Multi-agent frameworks (CrewAI, LangGraph):** Generic orchestration, not tailored to BMAD's specific role/phase structure
- **Manual scripting:** Brittle, requires maintenance, no standardization

### Proposed Solution

**bmad-auto** provides a single command that:
1. Reads an epic file from the target repository
2. Orchestrates the story loop (SM → Dev → Review → iterate → Commit)
3. Persists state for pause/resume
4. Outputs reviewed, committed code

**MVP Scope:**
- Story loop: Scrum Master → Developer → Reviewer (iterate until approved) → Commit
- Claude Code only (Codex support deferred)
- Headless mode (TUI deferred)
- Single epic targeting

### Key Differentiators

| Pain Point | bmad-auto Solution |
|------------|-------------------|
| Context switching | Orchestrator manages all context passing |
| Repetitive prompts | Role prompts are templated and automatic |
| Role friction | Single command, roles invoked internally |
| Lost progress | State persisted to JSON, resumable |
| No visibility | Structured logging, status command |

---

## Target Users

### Primary User: The Solo AI-Augmented Developer

**Persona: "Warm" - The Autonomous Builder**

- **Context:** Solo developer, freelancer, and side-project enthusiast who also uses AI-assisted development in their day job
- **Environment:** Works on multiple projects; values time efficiency and automation
- **BMAD Usage:** Already familiar with BMAD methodology and its agent-role structure

**Current Pain:**
- Manually orchestrates BMAD agents during development sessions
- Context switching between role-specific commands breaks flow
- Can't step away from the keyboard during long implementation sessions
- Loses track of progress across stories and epics

**Key Desire:**
> "I want to kick off an epic and walk away. When I come back, the code should be implemented and reviewed—or at least I should know exactly where it stopped and why."

**Success Looks Like:**
- Start bmad-auto on an epic before bed or during lunch
- Return to find committed, reviewed code (or clear status on what needs attention)
- Resume seamlessly if interrupted

### Secondary Users

**Other BMAD Practitioners:**
- Developers who've adopted BMAD methodology and want to reduce manual orchestration overhead
- May discover bmad-auto through BMAD community or GitHub

**Automation-Seeking Developers:**
- Developers frustrated with manual AI-agent orchestration (even if not using BMAD specifically)
- Looking for structured, repeatable AI-assisted workflows

### Anti-Users (Explicitly Not For)

- **Non-BMAD users:** The tool assumes familiarity with BMAD's epic/story structure
- **Manual-control purists:** Those who prefer direct, interactive control over each agent invocation
- **Teams (for now):** MVP focuses on single-developer workflows; team features deferred

### User Journey

**Discovery:** Finds bmad-auto via BMAD documentation, GitHub, or word-of-mouth from other AI-assisted developers

**Onboarding:**
1. `uvx bmad-auto init` in target repo
2. Configure agent settings (or use defaults)
3. Point at first epic file

**Core Usage:**
1. Run `uvx bmad-auto run --epic docs/epics/epic-001.md`
2. Optionally monitor progress or walk away
3. Return to check status / review committed code

**Success Moment:** First time returning to find a fully implemented and reviewed story committed—without manual intervention

**Long-term:** bmad-auto becomes the default way to execute BMAD implementation phases; manual orchestration becomes the exception

---

## Success Metrics

### User Success Criteria

**bmad-auto is working when:**

1. **Autonomous Execution** - A story loop completes without manual intervention (SM → Dev → Review → Commit)
2. **Reliable Resume** - Workflow resumes seamlessly after interruption with no lost progress
3. **AFK Capability** - A full epic can be processed while the user is away from keyboard
4. **Trust Threshold** - User reaches for bmad-auto by default instead of manual BMAD orchestration

### Failure Scenarios to Prevent

| Failure Mode | Prevention Criteria |
|--------------|---------------------|
| Corrupted code | All committed code must pass review phase; no silent failures |
| Lost progress | State persisted after every phase; resume always works |
| Unclear status | User can always determine exactly where workflow stopped and why |
| Wasted time | Failures surface early; no long runs that produce unusable output |

### Key Performance Indicators

| KPI | Target | Measurement |
|-----|--------|-------------|
| Story completion rate | >90% of stories complete without manual intervention | Completed stories / Total stories attempted |
| Resume reliability | 100% successful resume after interruption | Failed resumes / Total resume attempts |
| Time to first value | <5 minutes from install to first successful story | Time from `uvx bmad-auto init` to first commit |
| Review loop efficiency | <3 review iterations per story on average | Total review attempts / Completed stories |

### Business Objectives

**Not applicable** - This is a personal productivity tool. Community adoption (GitHub stars, external contributors) is not a success metric.

Success is measured purely by: **"Does it save me time and work reliably?"**

---

## MVP Scope

### Core Features

**CLI Commands:**
| Command | Purpose |
|---------|---------|
| `bmad-auto run --epic <file>` | Execute story loop for an epic |
| `bmad-auto status` | Check current workflow progress |
| `bmad-auto resume` | Continue a paused/interrupted workflow |

**Story Loop:**
```
Epic File → SM creates story → Dev implements → Reviewer checks
                    ↑__________________________________|
                          (iterate until APPROVED)
                                    ↓
                            Auto-commit to branch
```

**Core Capabilities:**
- Parse BMAD epic files and extract story requirements
- Invoke Claude Code CLI with role-specific prompts (SM, Dev, Reviewer)
- Pass context between agents via orchestrator-managed state
- Persist workflow state to JSON for pause/resume
- Auto-create feature branch for epic
- Auto-commit after each approved story

**Integration:**
- Claude Code CLI only (via Claude Agent SDK)
- Headless mode (structured logging to terminal)

### Out of Scope for MVP

| Feature | Rationale |
|---------|-----------|
| TUI dashboard | Nice-to-have; headless logging sufficient for MVP |
| Codex CLI support | Simplify integration; add later |
| `bmad-auto init` command | Manual config file creation acceptable |
| Auto-create PR | User can run `gh pr create` manually |
| Tech Writer phase | Focus on core dev loop first |
| Retrospective phase | Focus on core dev loop first |
| Multi-epic parallel | Single epic sufficient for MVP |

### MVP Success Criteria

MVP is successful when:
1. User can run `bmad-auto run --epic <file>` and walk away
2. Stories complete autonomously (SM → Dev → Review → Commit)
3. Workflow resumes correctly after interruption
4. User returns to find committed, reviewed code

### Future Vision

**Post-MVP Enhancements:**
- TUI dashboard for real-time progress visualization
- Codex CLI support for model diversity
- `bmad-auto init` for guided setup
- Auto-PR creation with summary
- Tech Writer and Retrospective phases
- Multi-epic parallel processing
- Team collaboration features (long-term)

---

*Product Brief completed: 2025-12-25*
