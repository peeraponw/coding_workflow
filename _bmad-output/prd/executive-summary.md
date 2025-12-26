# Executive Summary

**bmad-auto** is a uvx-installable CLI tool that automates the implementation phase of the BMAD methodology. It eliminates manual orchestration overhead by providing single-command epic execution with intelligent agent coordination.

**The Core Problem:**
Manual BMAD orchestration requires dozens of CLI invocations per epic—context switching between agents, copying outputs, tracking progress mentally. The cognitive overhead often exceeds the methodology's value.

**The Solution:**
One command. One epic. Reviewed code.

```bash
uvx bmad-auto run --epic docs/epics/epic-001.md
```

The orchestrator manages the story loop: Scrum Master creates stories → Developer implements → Reviewer validates → iterate until approved → auto-commit. State persists to YAML for pause/resume capability.

## What Makes This Special

1. **Hierarchical Model Routing** - Higher-tier models (Claude) judge and control; lower-tier models (GLM) execute implementation. Cost-efficient without sacrificing quality gates.

2. **AFK-Friendly Execution** - Kick off an epic before lunch, return to committed, reviewed code. No babysitting required.

3. **Seamless Pause/Resume** - YAML state persistence means interruptions don't lose progress. Pick up exactly where you left off.

4. **Trust Through Review Gates** - Every commit passes the SM → Dev → Review loop. No silent failures, no corrupted code.
