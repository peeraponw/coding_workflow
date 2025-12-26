# CLI Tool Specific Requirements

## Command Structure

**Core Commands (MVP):**

| Command | Purpose | Example |
|---------|---------|---------|
| `bmad-auto run --epic <file>` | Execute story loop for an epic | `bmad-auto run --epic docs/epics/epic-001.md` |
| `bmad-auto status` | Check current workflow progress | `bmad-auto status` |
| `bmad-auto resume` | Continue paused/interrupted workflow | `bmad-auto resume` |

**Command Behavior:**
- All commands are non-interactive (headless)
- No TUI or interactive prompts
- Designed for scriptability and automation

## Output Formats

**Terminal Output (Logs):**
- Plain text, human-readable logs
- Structured workflow progression showing:
  - Current agent (SM, Dev, Reviewer)
  - Current action and status
  - Handoff reasons between agents
  - Next agent in sequence
- Timestamped entries for debugging

**Example Log Output:**
```
[14:23:07] WORKFLOW: Starting epic docs/epics/epic-001.md
[14:23:08] SM: Creating story 1 of 5...
[14:25:12] SM: Story created - "Add user authentication endpoint"
[14:25:12] HANDOFF: SM → Dev (story ready for implementation)
[14:25:13] DEV: Implementing story...
[14:32:45] DEV: Implementation complete (3 files modified)
[14:32:45] HANDOFF: Dev → Reviewer (code ready for review)
[14:32:46] REVIEWER: Reviewing implementation...
```

**Inter-Agent Communication:**
- YAML format for agent handoff files (human-readable, token-efficient)
- State persistence in YAML format (`.bmad-auto-state.yaml`)
- Consistent format across all orchestrator-managed files

## Configuration Schema

**Config File:** `.bmad-auto.yaml` in project root

```yaml
workflow:
  epic_path: "docs/epics"
  state_file: ".bmad-auto-state.yaml"

agents:
  sm_model: "claude"               # Uses logged-in Anthropic subscription
  dev_model: "glm"                 # Uses GLM via ANTHROPIC_BASE_URL
  reviewer_model: "claude"         # Uses logged-in Anthropic subscription

git:
  auto_branch: true
  auto_commit: true
  branch_prefix: "epic/"
```

**Environment Variables (GLM only):**
- `ANTHROPIC_API_KEY` - Required only for GLM-routed agents
- `ANTHROPIC_BASE_URL` - Required only for GLM-routed agents

**Authentication:**
- Claude agents: Use logged-in Anthropic subscription (no API key needed)
- GLM agents: Require `ANTHROPIC_API_KEY` + `ANTHROPIC_BASE_URL` environment variables

## Scripting Support

**Exit Codes:**

| Code | Meaning |
|------|---------|
| 0 | Success - workflow completed |
| 1 | Error - workflow failed (see logs) |
| 2 | Paused - workflow paused, resumable |
| 3 | Config error - invalid configuration |

**Automation-Friendly:**
- No interactive prompts
- Clear exit codes for CI/CD integration
- Structured logging for log aggregation
- `--json` flag for machine-parseable status output (Growth feature)
