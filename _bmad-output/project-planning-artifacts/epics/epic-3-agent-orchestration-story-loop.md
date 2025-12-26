# Epic 3: Agent Orchestration & Story Loop

User can execute the full SM → Dev → Review → Commit loop automatically.

**FRs covered:** FR5-11

## Story 3.1: Agent Protocol & Base Implementation

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

## Story 3.2: Claude Agent Adapter

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

## Story 3.3: Agent Command Builder

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

## Story 3.4: Model Routing Configuration

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

## Story 3.5: Story Loop Orchestrator

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

## Story 3.6: Context Passing via YAML Handoff

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
