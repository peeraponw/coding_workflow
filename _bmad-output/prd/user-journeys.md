# User Journeys

## Journey 1: The Lunchtime Epic (Success Path)

Warm has just finished the planning phase for a new feature in his side project. The epic file is ready: five stories covering a new API endpoint with validation, tests, and documentation. It's 11:45 AM, and his stomach is growling.

Instead of the usual ritual—invoke SM, copy output, invoke Dev, wait, copy output, invoke Reviewer, iterate, commit, repeat—Warm types a single command:

```bash
uvx bmad-auto run --epic docs/epics/epic-001-user-auth.md
```

The terminal shows the orchestrator spinning up. "Story 1 of 5: SM creating story..." He grabs his jacket and heads to lunch.

Forty-five minutes later, Warm returns with a coffee. He glances at the terminal: "Story 4 of 5: Review approved. Committing..." The feature branch has three clean commits already. By the time he's finished his coffee, all five stories are done. He runs `git log --oneline` and sees exactly what he hoped for—five atomic commits, each reviewed and approved.

**The breakthrough moment:** Warm realizes he just shipped a feature while eating pad thai. The cognitive load of BMAD orchestration is gone.

## Journey 2: The 3 AM Rate Limit (Failure/Recovery Path)

Warm kicks off a complex refactoring epic before bed. Six stories, touching core modules. He sets his laptop on the desk and goes to sleep.

At 3 AM, the Claude API hits a rate limit mid-story. The orchestrator detects the failure, persists state to YAML, and logs clearly:

```
[03:14:22] ERROR: Rate limit exceeded (429)
[03:14:22] State saved: story-3, phase: dev, iteration: 2
[03:14:22] Workflow paused. Run 'bmad-auto resume' to continue.
```

Warm wakes up at 7 AM and sees the pause notification. No panic—the state file shows exactly where it stopped. Stories 1 and 2 are committed. Story 3's dev phase was mid-iteration.

He waits an hour for rate limits to reset, then runs `bmad-auto resume`. The orchestrator picks up exactly where it left off. By breakfast, the epic is complete.

**The breakthrough moment:** A failure at 3 AM didn't cost him anything. No corrupted state, no lost work, no guessing. Just resume and continue.

## Journey 3: The Anxious Check-In (Status Monitoring Path)

Warm has a big demo tomorrow. He kicked off an epic an hour ago but keeps wondering: "Is it working? How far along is it?"

Instead of interrupting the workflow, he opens a new terminal and runs `bmad-auto status`:

```
Epic: docs/epics/epic-003-dashboard.md
Status: IN_PROGRESS
Progress: Story 3 of 4

Current Story: "Add chart filtering"
  Phase: review (iteration 1)
  Started: 14:23:07
  Duration: 12m 34s

Completed Stories:
  ✓ Story 1: "Dashboard layout" - committed (abc123)
  ✓ Story 2: "Data fetching" - committed (def456)
```

Warm exhales. Three-quarters done, review phase, no errors. He goes back to his documentation, confident he'll have working code for tomorrow's demo.

**The breakthrough moment:** Visibility without interruption. He knows exactly where things stand without breaking his focus.

## Journey Requirements Summary

| Capability Area | Revealed By |
|-----------------|-------------|
| `run --epic` command | Journey 1 |
| Story loop orchestration (SM → Dev → Review → Commit) | Journey 1 |
| Auto-commit to feature branch | Journey 1 |
| Headless execution with structured logging | Journey 1, 2 |
| Error detection and graceful pause | Journey 2 |
| YAML state persistence | Journey 2 |
| `resume` command with exact state recovery | Journey 2 |
| Clear error messaging | Journey 2 |
| `status` command | Journey 3 |
| Progress reporting (story/phase/iteration) | Journey 3 |
| Non-blocking status checks | Journey 3 |
