# bmad-auto - Project Overview

**Type:** CLI Tool
**Language:** Python 3.13+
**Framework:** Typer + Rich
**Status:** MVP Complete (5 epics, 23 stories)

---

## Executive Summary

`bmad-auto` is an AI-powered development workflow orchestrator that automates the BMAD (Breakthrough Method for Agile AI-Driven Development) methodology. It orchestrates Claude Code CLI to execute story-driven development loops with specialized agent roles.

**Core Philosophy:**
- Pure Python orchestrator with Claude Agent SDK integration
- Rich terminal UI for live progress visualization
- Callable from any repository as an external tool
- State persistence per-repository with atomic writes
- Strict adherence to Python 3.13+ standards and vertical slice architecture

---

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Runtime | Python | >=3.13 | Core language |
| CLI Framework | Typer | >=0.21.0 | Command-line interface |
| Console UI | Rich | >=14.2.0 | Terminal formatting and display |
| Async | anyio | >=4.12.0 | Async runtime (matches Claude Agent SDK) |
| AI Integration | Claude Agent SDK | >=0.1.18 | Agent execution (uses Claude Code subscription) |
| Validation | Pydantic | >=2.12.5 | Data models |
| Config | pydantic-settings | >=2.12.0 | Environment and settings |
| Config Files | PyYAML | >=6.0.3 | User configuration |
| Logging | structlog | >=25.5.0 | Structured logging |
| Build | hatchling | - | Package building |
| Testing | pytest, pytest-asyncio | latest | Test framework |
| Linting | ruff, pyright | latest | Code quality |

---

## Architecture Overview

```
bmad-auto
├── CLI Layer (Typer)
│   └── Commands: run, status, resume
│
├── Orchestrator Layer
│   └── SM → Dev → Review loop with state transitions
│
├── Agent Layer
│   └── Protocol-based agents with Claude adapter
│
├── Infrastructure Layer
│   ├── State persistence (YAML with atomic writes)
│   ├── Git operations (subprocess wrapper)
│   └── Configuration (3-layer: internal/user/secrets)
│
└── Display Layer (Rich)
    └── Status display and progress reporting
```

---

## Key Features

1. **Workflow Orchestration** - Executes epic-driven development with SM→Dev→Review loop
2. **State Persistence** - Resume capability with atomic YAML writes
3. **Git Integration** - Auto-branch creation, auto-commit on review approval
4. **Progress Monitoring** - Rich terminal display with status command
5. **Error Recovery** - Graceful handling with pause/resume support

---

## Quick Reference

| Aspect | Details |
|--------|---------|
| Entry Point | `bmad-auto` → `bmad_auto.main:app` |
| Config File | `.bmad-auto.yaml` |
| State File | `.bmad-auto-state.yaml` |
| Exit Codes | 0=success, 1=error, 2=paused, 3=config_error |
| Authentication | Claude Code subscription (default) or API key (headless) |

---

## Related Documentation

- [Source Tree Analysis](./source-tree-analysis.md)
- [Architecture Guide](./architecture.md)
- [Development Guide](./development-guide.md)
- [PRD](./../_bmad-output/prd/index.md)
- [Architecture Decisions](./../_bmad-output/architecture/index.md)
- [Epics & Stories](./../_bmad-output/project-planning-artifacts/epics/index.md)
