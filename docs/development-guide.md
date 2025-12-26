# Development Guide

## Prerequisites

- Python 3.13+
- uv (package manager)
- Git

---

## Quick Start

```bash
# Clone and enter project
cd coding_workflow

# Create virtual environment and install dependencies
uv venv
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Type check
uv run pyright src/

# Lint and format
uv run ruff check .
uv run ruff format .
```

---

## Project Commands

| Command | Purpose |
|---------|---------|
| `uv sync` | Install/update dependencies |
| `uv run pytest` | Run tests |
| `uv run pytest --cov=src` | Run with coverage |
| `uv run pyright src/` | Type checking |
| `uv run ruff check .` | Linting |
| `uv run ruff format .` | Formatting |

---

## CLI Usage

```bash
# Run workflow for an epic
bmad-auto run --epic path/to/epic.md

# Check workflow status
bmad-auto status

# Resume paused workflow
bmad-auto resume
```

---

## Code Organization

### Adding a New Feature

1. Create feature directory under `features/`:
   ```
   features/new_feature/
   ├── __init__.py
   ├── handler.py
   └── tests/
       └── test_handler.py
   ```

2. Export public API from `__init__.py`

3. Add tests in co-located `tests/` directory

### Adding Constants

All constants go in `shared/consts.py`:

```python
# shared/consts.py
NEW_CONSTANT: Final[str] = "value"
```

### Adding Exceptions

All exceptions go in `shared/exceptions.py`:

```python
# shared/exceptions.py
class NewError(BmadAutoError):
    """Description of when this is raised."""
    pass
```

---

## Code Standards (from AGENTS.md)

### File Limits
- Files: max 500 lines
- Functions: max 50 lines
- Classes: max 100 lines
- Line length: max 100 characters

### Import Rules
- **NO relative imports** - always use absolute
- Example: `from bmad_auto.shared.consts import EXIT_SUCCESS`

### Type Hints
- Required on all public functions
- NO `TYPE_CHECKING` imports

### Logging
- Use structlog (configured in `shared/logging.py`)
- NO print statements in production code

### Error Handling
- Define domain-specific exceptions
- Never swallow errors silently
- Fail fast with explicit messages

---

## Testing Strategy

### Test Location
Tests are co-located with source code:
```
core/
├── state.py
└── tests/
    └── test_state.py
```

### Coverage Requirement
- Minimum: 80%
- New code must not reduce coverage

### Test Rules
- Use pytest (not unittest)
- Mock external dependencies
- Use fixtures from `conftest.py`

### Running Specific Tests
```bash
# Run single test file
uv run pytest src/bmad_auto/core/tests/test_state.py

# Run tests matching pattern
uv run pytest -k "test_load"

# Run with verbose output
uv run pytest -v
```

---

## Configuration

### User Config (`.bmad-auto.yaml`)

```yaml
workflow:
  epic_path: "path/to/epic.md"
  state_file: ".bmad-auto-state.yaml"

agents:
  sm_model: "claude-sonnet-4-20250514"
  dev_model: "claude-sonnet-4-20250514"
  reviewer_model: "claude-sonnet-4-20250514"

git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```

### Authentication

**Default Mode (Subscription):**
Uses Claude Code desktop credentials - no API key needed.

```bash
# Ensure Claude Code is logged in
claude login
```

**Headless Mode (CI/Automation):**
Only for environments without Claude Code login.

```bash
# .env (only for headless execution)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_BASE_URL=https://api.anthropic.com  # optional
```

---

## Pre-Commit Checklist

Before committing:

- [ ] `uv sync` run and lockfile updated
- [ ] `uv run ruff format .` applied
- [ ] `uv run ruff check .` passes
- [ ] `uv run pyright src/` passes
- [ ] `uv run pytest` passes
- [ ] Coverage >= 80%
- [ ] No print statements
- [ ] No relative imports
- [ ] No magic strings (use constants)
- [ ] No secrets in code

---

## Git Workflow

### Branch Naming
- `feat/*` - features
- `fix/*` - bug fixes
- `docs/*` - documentation
- `refactor/*` - refactors

### Commit Messages
```
feat(auth): add jwt-based login
fix(api): handle invalid pagination params
docs(readme): update setup instructions
```

---

## Troubleshooting

### Tests Failing
```bash
# Run with verbose output
uv run pytest -v --tb=short

# Run single failing test
uv run pytest path/to/test.py::test_name -v
```

### Type Errors
```bash
# Check specific file
uv run pyright src/bmad_auto/core/state.py
```

### Import Errors
- Ensure you're using absolute imports
- Check `__init__.py` exports
- Verify package is installed: `uv sync`

---

## References

- [AGENTS.md](../src/AGENTS.md) - Full development standards
- [Project Context](../_bmad-output/project-context.md) - bmad-auto specific rules
