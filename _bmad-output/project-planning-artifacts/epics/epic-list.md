# Epic List

## Epic 1: Project Foundation & CLI Entry Points
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

## Epic 2: State Persistence & Resume Capability
User can pause/interrupt a workflow and resume exactly where they left off.

**FRs covered:** FR3, FR4, FR12-16, FR34

**Scope:**
- Epic file parsing
- YAML state persistence (atomic writes)
- Resume from exact interruption point
- Graceful error recovery (rate limits, API errors)
- State integrity preservation

---

## Epic 3: Agent Orchestration & Story Loop
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

## Epic 4: Progress Monitoring & Logging
User can check workflow status without interrupting execution.

**FRs covered:** FR17-21

**Scope:**
- `status` command shows current progress
- Timestamped terminal logging
- Agent handoff visibility (from → to → reason)
- Completed stories with commit references
- Non-blocking status checks

---

## Epic 5: Git Integration & Auto-Commit
User returns to find committed, reviewed code on a feature branch.

**FRs covered:** FR22-25

**Scope:**
- Auto-create feature branch for epic
- Auto-commit after each story passes review
- Story reference in commit messages
- Configurable branch naming prefix

---
