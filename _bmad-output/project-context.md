---
project_name: 'bmad-auto'
user_name: 'Warm'
date: '2025-12-26'
extends: 'src/AGENTS.md'
status: 'complete'
---

# Project Context: bmad-auto

_bmad-auto specific rules that extend AGENTS.md. For general Python rules, see `src/AGENTS.md`._

---

## Technology Stack

- **Python:** 3.11+
- **CLI:** Typer with Rich (typer[all])
- **Async:** anyio (matches Claude Agent SDK)
- **Config:** pydantic-settings (internal) + pyyaml (user config)
- **Logging:** structlog + Rich console
- **Build:** hatchling, uvx distribution
- **Testing:** pytest, pytest-asyncio, 80% coverage

---

## Critical bmad-auto Rules

### Agent Invocation Pattern

**MUST:** Invoke bmad agents via skill commands, not raw prompts.

```python
# ✅ Correct: Use bmad skill commands
await agent.run("/bmad:bmm:agents:sm create stories from epics 02")
await agent.run("/bmad:bmm:agents:dev implement story-03")

# ❌ Wrong: Don't build prompts directly
await agent.run("You are an SM agent. Create stories...")
```

### Three-Layer Configuration (No Overlap)

| Layer | File | Purpose |
|-------|------|---------|
| Internal | pydantic_settings | Timeouts, retries (pre-distribution) |
| User | `.bmad-auto.yaml` | Epic path, models, git settings (runtime) |
| Secrets | `.env` | API keys (runtime, no BMAD_ prefix) |

**MUST NOT:** Mix config concerns. Internal settings don't go in user YAML.

### State Persistence

**MUST:** Persist state after each phase completion (SM done, Dev done, Review done).

**MUST:** Use atomic writes (write temp file, then rename).

```python
# ✅ Correct: Atomic write pattern
temp_path = state_path.with_suffix('.tmp')
temp_path.write_text(yaml.dump(state))
temp_path.rename(state_path)

# ❌ Wrong: Direct write (can corrupt on crash)
state_path.write_text(yaml.dump(state))
```

### Orchestrator Boundaries

**Orchestrator OWNS:**
- Workflow state transitions
- Agent context injection
- Phase sequencing (SM → Dev → Review → Git)

**Orchestrator DELEGATES TO:**
- `agents/` - Agent execution
- `state.py` - YAML file I/O
- `git_integration/` - Git CLI operations

**MUST NOT:** Put file I/O or git commands directly in orchestrator.

### CLI Exit Codes

| Code | Constant | Meaning | Resumable |
|------|----------|---------|-----------|
| 0 | `EXIT_SUCCESS` | Completed | N/A |
| 1 | `EXIT_ERROR` | Failed | Yes |
| 2 | `EXIT_PAUSED` | Paused (rate limit) | Yes |
| 3 | `EXIT_CONFIG_ERROR` | Bad config | No |

**MUST:** Return correct exit code from `main.py`. **MUST NOT:** Use bare integers.

### Logging vs Display

```python
# Logging (structlog) - for debugging/auditing
logger.info("Agent handoff", from_agent=AGENT_SM, to_agent=AGENT_DEV)

# Display (Rich) - for user-facing output
console.print("[blue]SM:[/blue] Creating story 1 of 5...")
```

**MUST NOT:** Use print() for either purpose.

---

## Anti-Patterns to Avoid

- **Direct prompt building:** Use bmad skill commands
- **Config layer mixing:** Keep internal/user/secrets separate
- **Non-atomic state writes:** Always use temp file + rename
- **Orchestrator doing I/O:** Delegate to state.py and git handler
- **Bare exit codes:** Use constants from `shared/consts.py`
- **print() statements:** Use structlog or Rich console

---

## Reference

- General Python rules: `src/AGENTS.md`
- Architecture decisions: `_bmad-output/architecture.md`
