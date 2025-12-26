# Success Criteria

## User Success

bmad-auto succeeds when users experience:

1. **Autonomous Execution** - A story loop completes without manual intervention (SM → Dev → Review → Commit)
2. **Reliable Resume** - Workflow resumes seamlessly after interruption with no lost progress
3. **AFK Capability** - A full epic can be processed while the user is away from keyboard
4. **Trust Threshold** - User reaches for bmad-auto by default instead of manual BMAD orchestration

**The "Worth It" Moment:** Returning from lunch to find committed, reviewed code—without having touched the keyboard.

## Business Success

This is a personal productivity tool. No revenue, growth, or adoption metrics apply.

**Success = "Does it save me time and work reliably?"**

Community adoption (GitHub stars, contributors) is not a success metric.

## Technical Success

1. **State Integrity** - YAML state accurately reflects workflow progress; never corrupted
2. **Clear Error Reporting** - On failure, user knows exactly where it stopped and why
3. **Graceful Degradation** - Technical failures (rate limits, API errors) pause and wait for user intervention rather than corrupting state
4. **Clean Recovery** - User can revert to last working commit if needed

## Measurable Outcomes

| KPI | Target | Measurement |
|-----|--------|-------------|
| Story completion rate | >90% without intervention | Completed / Attempted |
| Resume reliability | 100% successful | Failed resumes / Total attempts |
| Time to first value | <5 minutes | Install to first commit |
| Review loop efficiency | <3 iterations average | Review attempts / Completed stories |

**Failure Handling (the 10%):**
- Workflow pauses, reports failure reason
- State persisted at last successful phase
- User intervenes: retry, revert, or manual fix
- No silent failures or corrupted commits
