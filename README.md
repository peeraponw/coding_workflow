# bmad-auto

AI-powered development workflow orchestrator using BMAD methodology.

## Overview

`bmad-auto` is a CLI tool that automates the implementation phase of the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology. It orchestrates Claude Code CLI to execute story-driven development loops with specialized agent roles.

## Features

- **Workflow Orchestration** - Executes SM → Dev → Review loops for epic-driven development
- **State Persistence** - Resume capability with atomic YAML writes
- **Git Integration** - Auto-branch creation, auto-commit on review approval
- **Progress Monitoring** - Rich terminal display with status command

## Requirements

- Python 3.13+
- uv (package manager)
- Claude Code (logged in with subscription)

## Installation

```bash
# Clone repository
git clone <repo-url>
cd coding_workflow

# Install dependencies
uv sync
```

## Usage

```bash
# Run workflow for an epic
bmad-auto run --epic path/to/epic.md

# Check workflow status
bmad-auto status

# Resume paused workflow
bmad-auto resume
```

## Configuration

Create `.bmad-auto.yaml` in your project root:

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

**Authentication:**

By default, uses your Claude Code subscription credentials:

```bash
# Ensure Claude Code is logged in
claude login
```

For headless/CI execution only, set `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

## Development

```bash
# Run tests
uv run pytest

# Type check
uv run pyright src/

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Documentation

See [docs/index.md](docs/index.md) for full documentation.

## License

MIT
