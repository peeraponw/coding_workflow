# Epic 5: Git Integration & Auto-Commit

User returns to find committed, reviewed code on a feature branch.

**FRs covered:** FR22-25

## Story 5.1: Git Handler Module

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

## Story 5.2: Feature Branch Creation

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

## Story 5.3: Auto-Commit After Review Approval

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

## Story 5.4: Branch Naming Configuration

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
