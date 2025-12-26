# Epic 2: State Persistence & Resume Capability

User can pause/interrupt a workflow and resume exactly where they left off.

**FRs covered:** FR3, FR4, FR12-16, FR34

## Story 2.1: Epic File Parser

As a **user**,
I want **bmad-auto to parse my epic markdown files**,
So that **stories can be extracted and executed sequentially**.

**Acceptance Criteria:**

**Given** an epic file in standard BMAD markdown format:
```markdown
# Epic: User Authentication
# Story 1: User Registration
...acceptance criteria...
# Story 2: User Login
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

## Story 2.2: Workflow State Model

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

## Story 2.3: State Persistence with Atomic Writes

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

## Story 2.4: Resume Detection & Recovery

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

## Story 2.5: Graceful Error Recovery

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
