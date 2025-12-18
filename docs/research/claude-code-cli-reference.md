# Claude Code CLI Reference for bmad-auto Integration

**Source**: [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
**Date Researched**: December 2025

---

## Overview

Claude Code CLI is Anthropic's official command-line interface for interacting with Claude. It supports both interactive and non-interactive (print) modes, making it suitable for automation and subprocess invocation.

---

## Key Features for bmad-auto

### 1. Print Mode (`-p` / `--print`)

Print mode is the primary mode for automation and subprocess usage:

```bash
# Basic non-interactive execution
claude -p "explain this function"

# With JSON output for parsing
claude -p "query" --output-format json

# Process piped content
cat file.txt | claude -p "summarize"
```

**Key Characteristics:**
- Executes query and exits (non-interactive)
- Supports output formatting (`text`, `json`, `stream-json`)
- Compatible with piped input (stdin)
- Works with `--max-turns` to limit agentic iterations

---

### 2. Output Format Options

| Format | Description | Use Case |
|--------|-------------|----------|
| `text` | Plain text (default) | Human-readable output |
| `json` | Structured JSON | Scripting and automation |
| `stream-json` | JSONL streaming | Real-time progressive processing |

**JSON Output Example:**
```bash
claude -p "query" --output-format json
```

The JSON output includes:
- `result` - The agent's response text
- `session_id` - Session identifier for resume functionality
- `total_cost_usd` - API cost for the request

**Extracting session_id:**
```bash
sid=$(claude -p "Start a refactor session" --output-format json | jq -r '.session_id')
```

---

### 3. Session Management

#### Resume by ID or Name
```bash
claude --resume auth-refactor          # Resume by name
claude --resume abc123                 # Resume by ID
claude --resume                        # Interactive picker
```

#### Explicit Session ID
```bash
claude --session-id "550e8400-e29b-41d4-a716-446655440000"
```

#### Continue Most Recent
```bash
claude --continue      # or -c
claude -c -p "query"   # Continue via SDK (print mode)
```

#### Fork Sessions (create new from existing)
```bash
claude --resume abc123 --fork-session
```

**Important Note**: When repeatedly using `--continue` in non-interactive mode, it may create a new session that appears to resume but actually has a different ID. For automation, prefer using fixed `session_id` + `--resume`.

---

### 4. Turn Limits and Execution Control

```bash
# Limit agent iterations
claude -p --max-turns 3 "implement this feature"

# Fallback model when primary is overloaded
claude -p --fallback-model sonnet "query"
```

---

### 5. Permission Handling for Automation

```bash
# Skip permission prompts (use with caution)
claude -p --dangerously-skip-permissions "query"

# Use MCP tool for permission handling
claude -p --permission-prompt-tool mcp_auth_tool "query"
```

---

### 6. Structured Output with JSON Schema

```bash
claude -p --json-schema '{"type":"object","properties":{...}}' "query"
```

---

### 7. Debugging and Verbose Mode

```bash
# Full turn-by-turn output
claude --verbose -p "query"

# Debug specific categories
claude --debug "api,mcp" -p "query"
```

---

## Settings File Format (JSON)

Claude Code settings are stored in JSON format. Here's the structure for bmad-auto:

### High Tier Settings (Full permissions)
```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write(./src/**)",
      "Write(./tests/**)",
      "Write(./docs/**)",
      "Edit",
      "Bash(npm run *)",
      "Bash(pytest *)",
      "Bash(uv run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Bash(git commit *)",
      "Write(./.env*)"
    ],
    "defaultMode": "acceptEdits"
  },
  "model": "claude-sonnet-4-5-20250514"
}
```

### Low Tier Settings (Read-only)
```json
{
  "permissions": {
    "allow": [
      "Read(./src/**)",
      "Read(./tests/**)",
      "Read(./docs/**)",
      "Grep",
      "Glob"
    ],
    "deny": [
      "Write",
      "Edit",
      "Bash"
    ],
    "defaultMode": "default"
  },
  "model": "claude-haiku-4-5-20251001"
}
```

---

## Subprocess Integration Pattern

For bmad-auto, the recommended subprocess pattern:

```python
import asyncio
import json

async def run_claude_agent(prompt: str, settings_file: str, timeout: int = 600) -> dict:
    """Execute Claude Code CLI as subprocess."""
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "json",
        "--max-turns", "10",
    ]

    if settings_file:
        # Settings file is loaded automatically from ~/.claude/settings.json
        # or can be specified via environment
        pass

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
        raise AgentTimeoutError(f"Claude agent timed out after {timeout}s")

    if proc.returncode != 0:
        raise AgentExecutionError(f"Claude exited with code {proc.returncode}: {stderr.decode()}")

    return json.loads(stdout.decode())
```

---

## Error Handling Considerations

1. **Exit codes**: Non-zero exit code indicates failure
2. **Timeouts**: Use `asyncio.wait_for` to enforce timeouts
3. **Permission errors**: May occur if settings don't allow required operations
4. **Model overload**: Use `--fallback-model` for graceful degradation

---

## Session Storage

Claude Code stores sessions in JSONL format:
- Location: `~/.claude/sessions/` or similar
- Format: JSONL with message history
- Can be analyzed with tools like [ccusage](https://github.com/ryoppippi/ccusage)

---

## Sources

- [CLI Reference - Claude Code Docs](https://code.claude.com/docs/en/cli-reference)
- [Shipyard | Claude Code CLI Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [Mastering Claude Code Sessions](https://www.vibesparking.com/en/blog/ai/claude-code/docs/cli/2025-08-28-mastering-claude-code-sessions-continue-resume-automate/)
- [What is --output-format in Claude Code](https://claudelog.com/faqs/what-is-output-format-in-claude-code/)
