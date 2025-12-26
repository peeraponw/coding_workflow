# Epic 4: Progress Monitoring & Logging

User can check workflow status without interrupting execution.

**FRs covered:** FR17-21

## Story 4.1: Status Command Implementation

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

## Story 4.2: Timestamped Workflow Logging

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

## Story 4.3: Agent Handoff Logging

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

## Story 4.4: Progress Display with Commit References

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
