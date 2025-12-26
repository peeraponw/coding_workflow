# Story 3.4: Model Routing Configuration

Status: ready-for-dev

## Story

As a **user**,
I want **SM and Reviewer to use Claude, and Dev to use GLM**,
so that **I get quality gates from Claude while saving costs on implementation**.

## Acceptance Criteria

1. **Given** config specifies `agents.sm_model: "claude"`, `agents.dev_model: "glm"`, `agents.reviewer_model: "claude"`, **When** the orchestrator creates agents, **Then** SM agent uses logged-in Claude subscription (FR9), Dev agent uses GLM via ANTHROPIC_BASE_URL (FR10), and Reviewer agent uses logged-in Claude subscription (FR9)
2. **Given** GLM is configured for Dev, **When** Dev agent is created, **Then** it uses ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL from environment (FR27, FR28)
3. **Given** model config is invalid, **When** agent creation is attempted, **Then** ConfigError is raised with clear message
4. Tests verify routing for each model configuration
5. Credentials are never logged (NFR14)

## Tasks / Subtasks

- [ ] Task 1: Extend config for model routing (AC: 1-2)
  - [ ] Ensure agents section parsed from config
  - [ ] Support "claude" and "glm" model values
  - [ ] Load GLM credentials from environment
- [ ] Task 2: Create agent factory (AC: 1)
  - [ ] Implement `create_agent(role: AgentRole, config: Config) -> AgentProtocol`
  - [ ] Route based on config.agents.{role}_model
  - [ ] Return appropriate agent instance
- [ ] Task 3: Implement GLM agent variant (AC: 2)
  - [ ] Create ClaudeAgent with GLM endpoint configuration
  - [ ] Use ANTHROPIC_BASE_URL for API endpoint
  - [ ] Use ANTHROPIC_API_KEY for authentication
- [ ] Task 4: Implement validation (AC: 3)
  - [ ] Validate model values are "claude" or "glm"
  - [ ] Validate GLM credentials available when needed
  - [ ] Raise ConfigError with helpful message
- [ ] Task 5: Write tests (AC: 4-5)
  - [ ] Test routing to Claude for SM
  - [ ] Test routing to GLM for Dev
  - [ ] Test routing to Claude for Reviewer
  - [ ] Test invalid model config
  - [ ] Verify no credential logging

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Never log credentials (NFR14)
- Model routing determined at agent creation time
- GLM uses same API protocol with different endpoint
- Factory pattern for agent creation

### Model Configuration

```yaml
# .bmad-auto.yaml
agents:
  sm_model: "claude"      # Uses logged-in Claude subscription
  dev_model: "glm"        # Uses ANTHROPIC_BASE_URL endpoint
  reviewer_model: "claude" # Uses logged-in Claude subscription
```

### Agent Factory Pattern

```python
def create_agent(role: AgentRole, config: Config) -> AgentProtocol:
    """Create agent with appropriate model routing."""
    model_name = getattr(config.agents, f"{role.value}_model")

    if model_name == "claude":
        return ClaudeAgent(use_logged_in=True)
    elif model_name == "glm":
        return ClaudeAgent(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            base_url=os.environ["ANTHROPIC_BASE_URL"]
        )
    else:
        raise ConfigError(f"Unknown model: {model_name}")
```

### Source Tree Components

```
src/bmad_auto/agents/
├── __init__.py      # Export create_agent factory
├── base.py
├── claude.py        # Support both Claude and GLM endpoints
└── tests/
    └── test_routing.py
```

### Testing Standards

- Mock environment variables for GLM tests
- Test each agent role routing
- Verify credentials not in log output

### References

- [Source: _bmad-output/project-planning-artifacts/epics/epic-3-agent-orchestration-story-loop.md#story-34-model-routing-configuration]
- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#configuration-architecture]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
