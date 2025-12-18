# OpenAI Codex CLI Reference for bmad-auto Integration

**Source**: [Codex CLI Documentation](https://developers.openai.com/codex/cli)
**Date Researched**: December 2025

---

## Overview

Codex CLI is OpenAI's lightweight coding agent that runs in the terminal. It supports both interactive mode and non-interactive `exec` mode for automation.

---

## Key Features for bmad-auto

### 1. Non-Interactive Mode (`codex exec`)

The `exec` command runs Codex non-interactively, suitable for automation:

```bash
# Basic execution
codex exec "summarize the repo structure"

# With JSON streaming output
codex exec --json "implement the feature" | jq ...

# Full auto mode with file edits
codex exec --full-auto "fix the bug"

# Output last message to file
codex exec -o output.txt "query"
```

---

### 2. JSON Streaming Output (`--json`)

The `--json` flag streams events as JSON Lines (JSONL) to stdout:

```bash
codex exec --json "query" | jq ...
```

#### Event Types

| Event | Description |
|-------|-------------|
| `thread.started` | Thread initiates or resumes |
| `turn.started` | Beginning of conversational turn |
| `turn.completed` | Turn completion with token usage |
| `turn.failed` | Turn failure with error details |
| `item.started` | Thread item lifecycle start |
| `item.updated` | Thread item update |
| `item.completed` | Thread item completion |
| `error` | Unrecoverable stream error |

#### Item Types

| Item Type | Description |
|-----------|-------------|
| `agent_message` | Assistant responses |
| `reasoning` | Thinking summaries |
| `command_execution` | Shell commands run by agent |
| `file_change` | Project file modifications |
| `mcp_tool_call` | Model Context Protocol tool invocations |
| `web_search` | Search operations |
| `todo_list` | Agent's evolving task plan |

#### Sample JSON Event Structure
```json
{
  "type": "turn.completed",
  "thread_id": "abc123",
  "usage": {
    "input_tokens": 1500,
    "cached_tokens": 500,
    "output_tokens": 800
  }
}
```

---

### 3. Default Output Behavior

- **stderr**: Streams activity/progress in real-time
- **stdout**: Only the final agent message (for piping)
- `-o`/`--output-last-message`: Write final message to file

---

### 4. Session Management

#### Resume Previous Sessions
```bash
# Resume by session ID
codex exec resume <SESSION_ID>

# Resume last session
codex exec resume --last
```

**Note**: Flags must be respecified for each invocation; only context persists.

#### Session Logging
Sessions are automatically logged to:
```
$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl
```

---

### 5. Approval Policies and Sandbox Modes

#### Approval Policies

| Policy | Description |
|--------|-------------|
| `untrusted` | Prompt before non-trusted commands |
| `on-failure` | Prompt if sandbox execution fails |
| `on-request` | Let model decide when escalation needed |
| `never` | Never prompt; auto-retry on failure |

#### Sandbox Modes

| Mode | Description |
|------|-------------|
| `read-only` | Read-only filesystem access (default) |
| `workspace-write` | CWD is writable |
| `danger-full-access` | Disables sandboxing entirely |

#### Quick Flags
```bash
# Enable file edits
codex exec --full-auto "query"

# Full access including network
codex exec --sandbox danger-full-access "query"
```

---

## Configuration File (TOML)

Codex configuration is stored in TOML format at `$CODEX_HOME/config.toml` (default: `~/.codex/config.toml`).

### High Tier Configuration
```toml
model = "o3"
approval_policy = "on-failure"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"
model_reasoning_summary = "detailed"

[history]
persistence = true
```

### Low Tier Configuration
```toml
model = "codex-mini"
approval_policy = "never"
sandbox_mode = "workspace-write"
model_reasoning_effort = "low"

[history]
persistence = false
```

### Full Configuration Reference

#### Model Settings
```toml
# Model selection
model = "gpt-5.1-codex-max"
model_provider = "openai"

# Reasoning settings (for o3, o4-mini, codex variants, gpt-5.1+)
model_reasoning_effort = "medium"  # minimal, low, medium, high, xhigh
model_reasoning_summary = "auto"   # auto, concise, detailed, none

# Output verbosity for GPT-5 models
model_verbosity = "medium"  # low, medium, high

# Custom context window
model_context_window = 128000
```

#### Execution Settings
```toml
# Approval policy
approval_policy = "on-failure"

# Sandbox mode
sandbox_mode = "workspace-write"

# Workspace write settings
[sandbox_workspace_write]
exclude_tmpdir_env_var = false
exclude_slash_tmp = false
writable_roots = ["/custom/path"]
network_access = false
```

#### Feature Flags
```toml
[features]
unified_exec = false           # PTY-backed execution
rmcp_client = false            # OAuth for HTTP MCP servers
apply_patch_freeform = false   # Freeform patch application
view_image_tool = true         # Image viewing
web_search_request = false     # Web searches
ghost_commit = false           # Ghost commits each turn
skills = false                 # Skill discovery
```

#### Network Tuning
```toml
[model_providers.openai]
request_max_retries = 4
stream_max_retries = 5
stream_idle_timeout_ms = 300000  # 5 minutes
```

---

## Subprocess Integration Pattern

For bmad-auto, the recommended subprocess pattern:

```python
import asyncio
import json

async def run_codex_agent(prompt: str, config_file: str, timeout: int = 600) -> dict:
    """Execute Codex CLI as subprocess."""
    cmd = [
        "codex", "exec",
        "--json",
        "--config", config_file,
        prompt,
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise AgentTimeoutError(f"Codex agent timed out after {timeout}s")

    if proc.returncode != 0:
        raise AgentExecutionError(f"Codex exited with code {proc.returncode}")

    # Parse JSONL output - look for turn.completed or agent_message
    result = {"success": False, "output": "", "usage": {}}
    for line in stdout.decode().strip().split('\n'):
        if not line:
            continue
        event = json.loads(line)
        if event.get("type") == "turn.completed":
            result["success"] = True
            result["usage"] = event.get("usage", {})
        elif event.get("type") == "item.completed" and event.get("item_type") == "agent_message":
            result["output"] = event.get("content", "")

    return result
```

---

## Error Handling

1. **Exit codes**: Non-zero indicates failure
2. **Timeouts**: Enforce via subprocess timeout
3. **`turn.failed` events**: Check in JSONL stream
4. **`error` events**: Indicate unrecoverable errors

---

## Sources

- [Codex CLI Reference](https://developers.openai.com/codex/cli/reference/)
- [Codex CLI Features](https://developers.openai.com/codex/cli/features/)
- [Codex exec.md Documentation](https://github.com/openai/codex/blob/main/docs/exec.md)
- [Codex config.md Documentation](https://github.com/openai/codex/blob/main/docs/config.md)
- [GitHub - openai/codex](https://github.com/openai/codex)
