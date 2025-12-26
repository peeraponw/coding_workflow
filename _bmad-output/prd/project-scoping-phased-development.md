# Project Scoping & Phased Development

## MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP
Solve the core problem (manual BMAD orchestration overhead) with minimal features. No platform plays, no revenue features—just "does this actually work for me?"

**Resource Requirements:** Solo developer

## MVP Feature Set (Phase 1)

**Core User Journeys Supported:**
- The Lunchtime Epic (success path) - full autonomous execution
- The 3 AM Rate Limit (failure/recovery) - graceful pause and resume
- The Anxious Check-In (status monitoring) - non-blocking progress visibility

**Must-Have Capabilities:**

| Capability | Rationale |
|------------|-----------|
| `run --epic` command | Core value proposition |
| Story loop orchestration | The entire workflow |
| Hierarchical model routing | Cost optimization |
| YAML state persistence | Pause/resume requirement |
| `status` command | AFK visibility |
| `resume` command | Recovery from interruption |
| Headless logging | Workflow transparency |
| `.bmad-auto.yaml` config | Agent model configuration |
| Auto-branch and auto-commit | Hands-off execution |

**Explicitly Out of MVP:**

| Feature | Reason |
|---------|--------|
| TUI dashboard | Headless logging sufficient |
| Codex CLI support | Simplify integration |
| `init` command | Manual config acceptable |
| Auto-PR creation | `gh pr create` works |
| Shell completion | Convenience, not essential |
| Worktree parallelism | Over-engineering for MVP |

## Post-MVP Features

**Phase 2 (Growth):**
- TUI dashboard for real-time progress visualization
- Codex CLI support for model diversity
- `bmad-auto init` for guided setup
- Auto-PR creation with summary
- Shell completion (bash/zsh/fish)
- `--json` flag for machine-parseable status output

**Phase 3 (Expansion):**
- Git worktree parallelism for speculative execution
- Tech Writer and Retrospective phases
- Multi-epic parallel processing

**Phase 4 (Vision):**
- Team collaboration features

## Risk Mitigation Strategy

**Technical Risks:**

| Risk | Mitigation |
|------|------------|
| Claude Agent SDK limitations | Research already done; SDK approach validated |
| Rate limiting during long epics | Graceful pause + resume; user waits and retries |
| State corruption | YAML format human-readable for manual recovery |

**Market Risks:**
Not applicable—personal productivity tool.

**Resource Risks:**

| Risk | Mitigation |
|------|------------|
| Limited dev time | Tight MVP scope; no scope creep |
| Burnout | AFK-friendly tool means less manual work |
