# Story 1.3: Configuration Loading

Status: done

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

- [x] Task 1: Create config module (AC: 1, 5)
  - [x] Create `src/bmad_auto/core/config.py`
  - [x] Implement InternalSettings with pydantic_settings (timeouts, retries)
  - [x] Implement UserConfig dataclass for YAML config
- [x] Task 2: Implement YAML config loading (AC: 1)
  - [x] Load `.bmad-auto.yaml` from project root
  - [x] Parse workflow section (epic_path, state_file)
  - [x] Parse agents section (sm_model, dev_model, reviewer_model)
  - [x] Parse git section (auto_branch, auto_commit, branch_prefix)
- [x] Task 3: Implement environment variable loading (AC: 2-3)
  - [x] Load ANTHROPIC_API_KEY from environment
  - [x] Load ANTHROPIC_BASE_URL from environment
  - [x] Ensure credentials are never written to files
- [x] Task 4: Implement validation and error handling (AC: 4)
  - [x] Raise ConfigError if YAML is missing
  - [x] Raise ConfigError if YAML is malformed
  - [x] Raise ConfigError if required fields missing
  - [x] Return EXIT_CONFIG_ERROR (3) on config failures
- [x] Task 5: Write tests (AC: 6)
  - [x] Test valid config loading
  - [x] Test missing config file
  - [x] Test invalid YAML syntax
  - [x] Test missing required fields
  - [x] Test environment variable loading

- [x] Task 6: Implement proper model naming and conditional credentials (AC: 2)
  - [x] Update model names to use specific format: `opus-4.5`, `sonnet-4.5`, `glm-4.7`
  - [x] Make `get_credentials()` conditional - only required when any agent uses `glm-*` model
  - [x] Add helper function `requires_glm_credentials(config: UserConfig) -> bool`
  - [x] Update tests to use proper model names
  - [x] Add test: credentials NOT required when no glm model configured
  - [x] Add test: credentials required when any agent uses glm-* model

### Review Follow-ups (AI) - Completed

- [x] [AI-Review][HIGH] Add test for `get_credentials()` raising ConfigError when ANTHROPIC_API_KEY unset [config.py:186]
- [x] [AI-Review][MEDIUM] Remove unused imports `BaseModel`, `Field` from config.py [config.py:14]
- [x] [AI-Review][MEDIUM] Remove unused imports `os`, `dataclass`, `ValidationError` from test_config.py [test_config.py:6-11]
- [x] [AI-Review][MEDIUM] Add tests for type validation error paths (e.g., workflow/agents/git not being dicts) [config.py:117,128,143,159]

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
  sm_model: "opus-4.5"               # Uses logged-in Anthropic subscription
  dev_model: "glm-4.7"               # Uses GLM via ANTHROPIC_BASE_URL
  reviewer_model: "sonnet-4.5"       # Uses logged-in Anthropic subscription
git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```

**Model Naming Convention:**
- Anthropic models: `opus-4.5`, `sonnet-4.5`, `haiku-3.5` (uses logged-in subscription)
- GLM models: `glm-4.7`, `glm-*` pattern (requires `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL`)

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

glm-4.7 (Claude Code)

### Debug Log References

None - implementation completed without issues.

### Completion Notes List

**Implementation Summary:**
- Created `src/bmad_auto/core/config.py` with three-layer configuration:
  - `InternalSettings`: pydantic_settings for internal defaults (timeouts, retries)
  - `UserConfig`: dataclasses for YAML config (workflow, agents, git)
  - `Credentials`: dataclass for environment variables (API keys, base URL)
- Implemented `load_user_config()` function with comprehensive validation:
  - File existence check
  - YAML syntax validation
  - Required section/field validation
  - Type safety with frozen dataclasses
- Implemented `get_credentials()` function for secure credential loading
- Implemented `requires_glm_credentials()` helper for conditional credential loading
- Updated model naming convention: `opus-4.5`, `sonnet-4.5`, `glm-4.7`
- All 18 tests pass (100% for new module)
- All 71 total tests pass (no regressions)

**Review Fixes Applied:**
- Added test for `get_credentials()` raising ConfigError when ANTHROPIC_API_KEY unset
- Removed unused imports from config.py (BaseModel, Field)
- Removed unused imports from test_config.py (os, dataclass, ValidationError)
- Added tests for type validation error paths (workflow/agents/git not being dicts)

**Task 6 Additions:**
- Model naming: Anthropic (`opus-4.5`, `sonnet-4.5`, `haiku-3.5`) vs GLM (`glm-4.7`, `glm-*`)
- Conditional credentials: only required when any agent uses glm-* model
- Added `requires_glm_credentials(config: UserConfig) -> bool` helper
- Tests for credential requirement detection

**Acceptance Criteria Met:**
- AC1: `.bmad-auto.yaml` loading and validation ✓
- AC2: `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` env var loading (conditional on glm-*) ✓
- AC3: Credentials never written to files ✓
- AC4: ConfigError raised with EXIT_CONFIG_ERROR (3) ✓
- AC5: Internal defaults from pydantic_settings ✓
- AC6: Tests cover all scenarios ✓

### File List

**New Files:**
- `src/bmad_auto/core/__init__.py`
- `src/bmad_auto/core/config.py`
- `src/bmad_auto/core/tests/__init__.py`
- `src/bmad_auto/core/tests/test_config.py`
