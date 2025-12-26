# Product Scope

## MVP - Minimum Viable Product

**Commands:**
- `bmad-auto run --epic <file>` - Execute story loop for an epic
- `bmad-auto status` - Check current workflow progress
- `bmad-auto resume` - Continue paused/interrupted workflow

**Core Capabilities:**
- Story loop: SM creates story → Dev implements → Reviewer validates → iterate → Commit
- Claude Code only (via Claude Agent SDK)
- Hierarchical model routing (Claude for SM/Reviewer, GLM for Dev via ANTHROPIC_BASE_URL)
- YAML state persistence for pause/resume
- Auto-create feature branch, auto-commit after approved stories
- Headless mode with structured logging

## Growth Features (Post-MVP)

- TUI dashboard for real-time progress visualization
- Codex CLI support for model diversity
- `bmad-auto init` for guided setup
- Auto-PR creation with summary
- Git worktree parallelism for speculative execution

## Vision (Future)

- Tech Writer and Retrospective phases
- Multi-epic parallel processing
- Team collaboration features
