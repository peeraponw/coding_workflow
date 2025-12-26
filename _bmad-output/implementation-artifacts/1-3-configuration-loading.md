# Story 1.3: Configuration Loading

Status: ready-for-dev

## Story

As a **user**,
I want **to configure bmad-auto via `.bmad-auto.yaml` and environment variables**,
so that **I can customize agent models, paths, and git behavior**.

## Acceptance Criteria

1. **Given** I have a `.bmad-auto.yaml` file in my project root with workflow, agents, and git sections, **When** I run any bmad-auto command, **Then** the configuration is loaded and validated
2. **Given** I set `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` environment variables, **When** configuration is loaded, **Then** GLM credentials are available for agent routing (FR27, FR28)
3. **Given** credentials are loaded, **Then** they are NOT stored in any config or state files (NFR12)
4. **Given** `.bmad-auto.yaml` is missing or invalid, **When** I run a bmad-auto command, **Then** I get a clear ConfigError with exit code 3 (EXIT_CONFIG_ERROR)
5. Internal defaults (timeouts, retries) come from pydantic_settings
6. Tests cover valid config, missing config, and invalid config scenarios

## Tasks / Subtasks

- [ ] Task 1: Create config module (AC: 1, 5)
  - [ ] Create `src/bmad_auto/core/config.py`
  - [ ] Implement InternalSettings with pydantic_settings (timeouts, retries)
  - [ ] Implement UserConfig dataclass for YAML config
- [ ] Task 2: Implement YAML config loading (AC: 1)
  - [ ] Load `.bmad-auto.yaml` from project root
  - [ ] Parse workflow section (epic_path, state_file)
  - [ ] Parse agents section (sm_model, dev_model, reviewer_model)
  - [ ] Parse git section (auto_branch, auto_commit, branch_prefix)
- [ ] Task 3: Implement environment variable loading (AC: 2-3)
  - [ ] Load ANTHROPIC_API_KEY from environment
  - [ ] Load ANTHROPIC_BASE_URL from environment
  - [ ] Ensure credentials are never written to files
- [ ] Task 4: Implement validation and error handling (AC: 4)
  - [ ] Raise ConfigError if YAML is missing
  - [ ] Raise ConfigError if YAML is malformed
  - [ ] Raise ConfigError if required fields missing
  - [ ] Return EXIT_CONFIG_ERROR (3) on config failures
- [ ] Task 5: Write tests (AC: 6)
  - [ ] Test valid config loading
  - [ ] Test missing config file
  - [ ] Test invalid YAML syntax
  - [ ] Test missing required fields
  - [ ] Test environment variable loading

## Dev Notes

### Architecture Patterns & Constraints

- **CRITICAL:** Three-layer configuration with NO overlap:
  - Internal: pydantic_settings (timeouts, retries)
  - User: `.bmad-auto.yaml` (epic path, models, git)
  - Secrets: `.env` (API keys - no BMAD_ prefix)
- Use pyyaml for YAML parsing
- ConfigError must be raised for all config failures

### Configuration Schema

```yaml
# .bmad-auto.yaml
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"
agents:
  sm_model: "claude"
  dev_model: "glm"
  reviewer_model: "claude"
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```

### Internal Defaults

```python
class InternalSettings(BaseSettings):
    default_timeout: int = 600
    max_retries: int = 3
```

### Source Tree Components

```
src/bmad_auto/core/
├── __init__.py
├── config.py       # InternalSettings + UserConfig loader
└── tests/
    └── test_config.py
```

### Testing Standards

- Use tmp_path fixture for test config files
- Test both happy path and error cases
- Ensure credentials are never in assertions

### References

- [Source: _bmad-output/architecture/implementation-patterns-consistency-rules.md#configuration-architecture]
- [Source: _bmad-output/project-context.md#three-layer-configuration-no-overlap]
- [Source: _bmad-output/architecture/project-structure-boundaries.md#file-purpose-summary]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
