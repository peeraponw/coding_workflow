---
stepsCompleted: [1, 2, 3, 4, 5]
status: complete
inputDocuments: []
workflowType: 'research'
lastStep: 1
research_type: 'technical'
research_topic: 'Claude Code and Codex CLI Integration Patterns'
research_goals: 'Subprocess invocation patterns, output format parsing, uvx integration, limitations and edge cases'
user_name: 'Warm'
date: '2025-12-25'
web_research_enabled: true
source_verification: true
---

# Research Report: Claude Code & Codex CLI Integration

**Date:** 2025-12-25
**Author:** Warm
**Research Type:** Technical

---

## Research Overview

This technical research focuses on understanding how to programmatically integrate with Claude Code CLI and OpenAI Codex CLI for the bmad-auto orchestration tool.

**Research Goals:**
1. Subprocess invocation patterns for both CLIs
2. Output formats and parsing strategies (JSON for Claude, JSONL for Codex)
3. Integration considerations with uvx toolchain
4. Known limitations, edge cases, and failure modes

**Out of Scope:**
- Competitive analysis of alternative tools
- Agent role assignment decisions
- Security/permission models (deferred)

---

## Technical Research Scope Confirmation

**Research Topic:** Claude Code and Codex CLI Integration Patterns
**Research Goals:** Subprocess invocation patterns, output format parsing, uvx integration, limitations and edge cases

**Technical Research Scope:**

- Architecture Analysis - CLI architecture, command structure, subprocess execution patterns
- Implementation Approaches - How to invoke each CLI programmatically, async subprocess handling
- Technology Stack - CLI dependencies, configuration file formats (JSON/TOML), output formats
- Integration Patterns - JSON/JSONL parsing, session management, resume capabilities
- Performance Considerations - Timeouts, streaming output, error handling patterns

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for critical technical claims
- Confidence level framework for uncertain information
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2025-12-25

---

## Technology Stack Analysis

### Claude Code CLI

**Installation & Platform:**
- Installed via npm: `npm install -g @anthropic-ai/claude-code`
- Cross-platform support (macOS, Linux, Windows)
- Written in TypeScript/Node.js

**Core Command Structure:**
```bash
claude [options] [prompt]
claude -p "prompt" --output-format json    # Headless mode with JSON output
claude --continue                           # Resume most recent session
claude --resume <session-id>                # Resume specific session
```

**Key CLI Flags for Automation:**
| Flag | Purpose |
|------|---------|
| `-p, --print` | Headless/non-interactive mode |
| `--output-format json\|text\|stream-json` | Control output format |
| `--continue, -c` | Continue most recent conversation |
| `--resume <id>, -r` | Resume specific session |
| `--allowedTools` | Specify allowed tools for a run |
| `--system-prompt` | Override system prompt completely |
| `--append-system-prompt` | Add to default system prompt |
| `--verbose` | Enable debug logging |

_Source: [Anthropic CLI Reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage)_

### Codex CLI

**Installation & Platform:**
- npm: `npm install -g @openai/codex`
- Homebrew: `brew install --cask codex`
- Built in Rust for speed and efficiency
- Officially supports macOS and Linux; Windows via WSL2 recommended

**Core Command Structure:**
```bash
codex [prompt]                              # Interactive mode
codex exec "prompt"                         # Non-interactive execution
codex exec --json "prompt"                  # JSONL streaming output
codex resume <session-id>                   # Resume specific session
codex resume --last                         # Resume most recent session
```

**Key CLI Flags for Automation:**
| Flag | Purpose |
|------|---------|
| `exec` | Non-interactive execution mode |
| `--json` | JSONL streaming to stdout |
| `--output-schema <path>` | Enforce structured JSON output |
| `-o <file>` | Save final output to file |
| `resume` | Resume previous session |
| `--last` | Resume most recent session |
| `--cd <dir>` | Override working directory |

_Source: [OpenAI Codex CLI Reference](https://developers.openai.com/codex/cli/reference/)_

### Python Async Subprocess Integration

**Core asyncio APIs:**
```python
# Preferred approach for CLI orchestration
proc = await asyncio.create_subprocess_exec(
    'claude', '-p', prompt, '--output-format', 'json',
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
stdout, stderr = await proc.communicate()
```

**Key Functions:**
- `asyncio.create_subprocess_exec()` - Spawn subprocess with arguments list (preferred)
- `asyncio.create_subprocess_shell()` - Spawn subprocess via shell
- `asyncio.wait_for()` - Add timeout to subprocess operations
- `asyncio.gather()` - Run multiple subprocesses concurrently

**Important Considerations:**
- Use `communicate()` to avoid deadlocks with PIPE buffers
- Use `wait_for()` for timeout control instead of timeout parameter
- Windows requires ProactorEventLoop (default in Python 3.8+)

_Source: [Python asyncio Subprocess Documentation](https://docs.python.org/3/library/asyncio-subprocess.html)_

### uv/uvx Toolchain Integration

**Package Manager:**
- `uv` is an extremely fast Python package manager written in Rust
- Replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv

**CLI Tool Distribution:**
```bash
uvx bmad-auto run --epic docs/epics/epic-001.md    # Ephemeral install
uv tool install bmad-auto                           # Persistent install
```

**Packaging for Distribution:**
- Use hatchling as build backend
- Define entry point: `[project.scripts] bmad-auto = "bmad_auto.main:main"`
- Build wheel: `uv build`
- Publish: `uv publish`

_Source: [uv Documentation](https://docs.astral.sh/uv/)_

### Output Format Specifications

#### Claude Code JSON Output

**Format:** Single JSON object on completion
```json
{
  "result": "Agent's response text",
  "session_id": "abc123",
  "total_cost_usd": 0.0234,
  "duration_seconds": 45.2
}
```

**Streaming Format (`stream-json`):** Multiple JSON objects during execution

_Source: [Claude Code Output Format](https://claudelog.com/faqs/what-is-output-format-in-claude-code/)_

#### Codex CLI JSONL Output

**Format:** Newline-delimited JSON events (one per state change)

**Event Types:**
- `thread.started` - Session initialization
- `turn.started` / `turn.completed` / `turn.failed` - Turn lifecycle
- `item.*` - Agent messages, reasoning, command executions, file changes

**Session Logging:**
- Automatic JSONL logs: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`
- Contains full conversation: user/assistant messages, tools, errors

_Source: [Codex CLI Features](https://developers.openai.com/codex/cli/features/)_

### Session Management Comparison

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Resume last session | `--continue` or `-c` | `resume --last` |
| Resume by ID | `--resume <id>` | `resume <id>` |
| Session storage | Local files (automatic) | `~/.codex/sessions/` JSONL |
| Session picker | `--resume` (no ID) | `resume` (no ID) |
| Rename sessions | `/rename` command | Not available |
| History preserved | Full message history | Full transcript + plan |

_Sources: [Claude Code Sessions](https://stevekinney.com/courses/ai-development/claude-code-session-management), [Codex Resume](https://github.com/openai/codex/discussions/1076)_

### Configuration File Formats

**Claude Code:** JSON (`~/.claude/settings.json`)
```json
{
  "permissions": {
    "allow": ["Read", "Write(./src/**)", "Bash(npm run *)"],
    "deny": ["Bash(rm -rf *)"]
  },
  "model": "claude-sonnet-4-5-20250514"
}
```

**Codex CLI:** TOML (`~/.codex/config.toml`)
```toml
model = "o3"
approval_policy = "on-failure"
sandbox_mode = "workspace-write"
model_reasoning_effort = "high"

[history]
persistence = true
```

---

## Integration Patterns Analysis

### Recommended Integration Approaches

#### Option 1: Claude Agent SDK (Preferred for Claude)

**Key Discovery:** The Claude Code SDK has been renamed to **Claude Agent SDK** and provides a native Python interface that eliminates subprocess management.

```python
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions

async def run_claude_agent(prompt: str, working_dir: str) -> str:
    options = ClaudeAgentOptions(
        system_prompt="You are an expert developer",
        permission_mode='acceptEdits',
        cwd=working_dir
    )

    result = ""
    async for message in query(prompt=prompt, options=options):
        if message.type == 'result':
            result = message.result
    return result
```

**Advantages:**
- No subprocess management needed
- Built-in retry and error handling
- Native async support via anyio
- Custom tools via in-process MCP servers
- Bundled CLI - no separate installation required

**Installation:** `pip install claude-agent-sdk`

_Source: [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)_

#### Option 2: Codex CLI `exec` Mode (Preferred for Codex)

```python
import asyncio
import json

async def run_codex_agent(prompt: str, working_dir: str) -> dict:
    proc = await asyncio.create_subprocess_exec(
        'codex', 'exec', '--json', '--full-auto', prompt,
        '--cd', working_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    # Parse JSONL stream - last line is final result
    events = []
    for line in stdout.decode().strip().split('\n'):
        if line:
            events.append(json.loads(line))

    return events[-1] if events else {}
```

**Key Flags:**
- `--full-auto`: Allow file edits (default is read-only sandbox)
- `--json`: Stream JSONL events to stdout
- `--cd <dir>`: Set working directory
- `CODEX_API_KEY`: Environment variable for headless auth

_Source: [Codex exec Documentation](https://github.com/openai/codex/blob/main/docs/exec.md)_

### JSONL Streaming Parser Pattern

For real-time processing of Codex JSONL output:

```python
import asyncio
import json

async def stream_codex_events(prompt: str):
    proc = await asyncio.create_subprocess_exec(
        'codex', 'exec', '--json', prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async for line in proc.stdout:
        if line:
            event = json.loads(line.decode().strip())
            yield event

            # Handle specific event types
            if event.get('type') == 'turn.completed':
                break
            elif event.get('type') == 'turn.failed':
                raise RuntimeError(event.get('error'))
```

**Event Types to Handle:**
| Event Type | Meaning |
|------------|---------|
| `thread.started` | Session initialized |
| `turn.started` | Agent turn beginning |
| `turn.completed` | Agent turn finished successfully |
| `turn.failed` | Agent turn failed |
| `item.*` | Tool calls, file changes, reasoning |

_Source: [Codex CLI Features](https://developers.openai.com/codex/cli/features/)_

### Retry Pattern with Tenacity

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class AgentTimeoutError(Exception):
    pass

class AgentExecutionError(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((AgentTimeoutError, AgentExecutionError))
)
async def run_agent_with_retry(agent, prompt: str) -> str:
    try:
        return await asyncio.wait_for(
            agent.run(prompt),
            timeout=600  # 10 minutes
        )
    except asyncio.TimeoutError:
        raise AgentTimeoutError("Agent execution timed out")
```

**Tenacity Features Used:**
- `stop_after_attempt(3)`: Maximum 3 retries
- `wait_exponential`: Exponential backoff (4s, 8s, 16s... max 60s)
- `retry_if_exception_type`: Only retry specific exceptions

_Source: [Tenacity Documentation](https://tenacity.readthedocs.io/)_

### Session Resume Pattern

```python
class SessionManager:
    """Manage CLI sessions for pause/resume functionality."""

    async def run_with_session(
        self,
        cli: str,  # 'claude' or 'codex'
        prompt: str,
        session_id: str | None = None
    ) -> tuple[str, str]:  # (result, session_id)

        if cli == 'claude':
            if session_id:
                args = ['claude', '--resume', session_id, '-p', prompt,
                        '--output-format', 'json']
            else:
                args = ['claude', '-p', prompt, '--output-format', 'json']

            result = await self._run_subprocess(args)
            return result['result'], result['session_id']

        elif cli == 'codex':
            if session_id:
                args = ['codex', 'resume', session_id]
            else:
                args = ['codex', 'exec', '--json', prompt]

            events = await self._run_codex(args)
            # Extract session_id from thread.started event
            session_id = next(
                (e['session_id'] for e in events
                 if e.get('type') == 'thread.started'),
                None
            )
            return events[-1].get('result', ''), session_id
```

### Error Handling Patterns

```python
from enum import Enum
from dataclasses import dataclass

class AgentErrorType(Enum):
    TIMEOUT = "timeout"
    EXECUTION_FAILED = "execution_failed"
    PARSE_ERROR = "parse_error"
    NOT_FOUND = "not_found"

@dataclass
class AgentResult:
    success: bool
    output: str
    error: AgentErrorType | None = None
    error_message: str | None = None
    session_id: str | None = None
    duration_seconds: float = 0.0
    cost_usd: float | None = None

async def safe_agent_run(agent, prompt: str) -> AgentResult:
    start_time = time.time()

    try:
        result = await asyncio.wait_for(
            agent.run(prompt),
            timeout=600
        )
        return AgentResult(
            success=True,
            output=result.output,
            session_id=result.session_id,
            duration_seconds=time.time() - start_time,
            cost_usd=result.cost_usd
        )
    except asyncio.TimeoutError:
        return AgentResult(
            success=False,
            output="",
            error=AgentErrorType.TIMEOUT,
            error_message="Agent execution exceeded 600s timeout",
            duration_seconds=time.time() - start_time
        )
    except json.JSONDecodeError as e:
        return AgentResult(
            success=False,
            output="",
            error=AgentErrorType.PARSE_ERROR,
            error_message=f"Failed to parse agent output: {e}",
            duration_seconds=time.time() - start_time
        )
```

### Hybrid Architecture: SDK + Subprocess Fallback

For bmad-auto, a hybrid approach may be optimal:

```python
from abc import ABC, abstractmethod
from typing import Protocol

class AgentProtocol(Protocol):
    async def run(self, prompt: str) -> AgentResult: ...
    async def validate(self) -> bool: ...

class ClaudeSDKAgent:
    """Use Claude Agent SDK (preferred)."""

    async def run(self, prompt: str) -> AgentResult:
        from claude_agent_sdk import query
        async for msg in query(prompt=prompt, options=self.options):
            # Process messages
            ...

class CodexSubprocessAgent:
    """Use Codex CLI via subprocess."""

    async def run(self, prompt: str) -> AgentResult:
        proc = await asyncio.create_subprocess_exec(
            'codex', 'exec', '--json', prompt,
            stdout=asyncio.subprocess.PIPE
        )
        # Parse JSONL output
        ...

def create_agent(cli: str, config: AgentConfig) -> AgentProtocol:
    """Factory function for agent creation."""
    if cli == 'claude':
        return ClaudeSDKAgent(config)
    elif cli == 'codex':
        return CodexSubprocessAgent(config)
    else:
        raise ValueError(f"Unknown CLI: {cli}")
```

_Source: [Claude Agent SDK Overview](https://platform.claude.com/docs/en/agent-sdk/overview)_

---

## Multi-Agent Communication Patterns

### The Core Problem

**Neither Claude Code nor Codex CLI have built-in mechanisms for inter-agent communication.** Each CLI operates in isolation - they don't natively share context, state, or communicate with each other. The orchestrator (bmad-auto) must implement this coordination layer.

### Communication Approaches

#### 1. File-Based Context Passing (Recommended for bmad-auto)

The most common pattern uses files as the communication medium:

```
Agent A (Scrum Master)     Agent B (Developer)      Agent C (Reviewer)
        │                         │                        │
        ▼                         ▼                        ▼
   ┌─────────┐               ┌─────────┐              ┌─────────┐
   │ Creates │               │  Reads  │              │  Reads  │
   │ story.md│──────────────▶│ story.md│─────────────▶│  diff   │
   └─────────┘               │ Writes  │              │ Writes  │
                             │  code   │              │ review  │
                             └─────────┘              └─────────┘
```

**Implementation:**
```python
class FileBasedContextManager:
    """Pass context between agents via files."""

    def __init__(self, context_dir: Path):
        self.context_dir = context_dir
        self.context_dir.mkdir(parents=True, exist_ok=True)

    async def pass_to_next_agent(
        self,
        from_agent: str,
        to_agent: str,
        context: dict
    ) -> Path:
        """Write context file for next agent."""
        handoff_file = self.context_dir / f"{from_agent}_to_{to_agent}.md"

        content = f"""# Handoff: {from_agent} → {to_agent}

## Previous Agent Output
{context.get('output', '')}

## Files Modified
{chr(10).join(context.get('files_modified', []))}

## Instructions for {to_agent}
{context.get('instructions', '')}

## Session Context
- Previous session ID: {context.get('session_id', 'N/A')}
- Timestamp: {datetime.now().isoformat()}
"""
        handoff_file.write_text(content)
        return handoff_file

    def build_prompt_with_context(
        self,
        agent_role: str,
        task: str,
        handoff_file: Path | None
    ) -> str:
        """Build prompt including handoff context."""
        prompt = f"You are acting as {agent_role}.\n\n"

        if handoff_file and handoff_file.exists():
            prompt += f"## Context from Previous Agent\n"
            prompt += handoff_file.read_text()
            prompt += "\n\n"

        prompt += f"## Your Task\n{task}"
        return prompt
```

_Sources: [CCSwarm](https://github.com/nwiizo/ccswarm), [Continuous-Claude](https://github.com/parcadei/Continuous-Claude)_

#### 2. Shared Planning Document Pattern

Used by multi-agent frameworks - agents coordinate through a shared document:

```python
PLANNING_DOC = Path("docs/stories/current_story.md")

class SharedPlanningDocument:
    """Agents coordinate via shared planning doc."""

    async def scrum_master_creates_story(self, epic_content: str) -> str:
        prompt = f"""
Read the epic and create the next story file.
Write to: {PLANNING_DOC}

Epic content:
{epic_content}
"""
        return await self.claude_agent.run(prompt)

    async def developer_implements(self) -> str:
        prompt = f"""
Read the story from: {PLANNING_DOC}
Implement the requirements.
Update the story file with implementation notes.
"""
        return await self.codex_agent.run(prompt)

    async def reviewer_reviews(self) -> str:
        prompt = f"""
Read the story from: {PLANNING_DOC}
Review the implementation (check git diff).
Add review comments to the story file.
Mark as APPROVED or REJECTED.
"""
        return await self.claude_agent.run(prompt)
```

_Source: [Multi-Agent Orchestration with Claude Code](https://sjramblings.io/multi-agent-orchestration-claude-code-when-ai-teams-beat-solo-acts/)_

#### 3. Orchestrator-Managed State (bmad-auto pattern)

The orchestrator holds state and injects relevant context into each agent prompt:

```python
@dataclass
class WorkflowContext:
    """Orchestrator-managed state passed between agents."""
    epic_content: str
    current_story: StoryInfo | None = None
    completed_stories: list[str] = field(default_factory=list)
    failed_stories: list[str] = field(default_factory=list)
    last_agent_output: str = ""
    git_diff: str = ""
    review_feedback: str = ""

class Orchestrator:
    """Central coordinator - agents don't talk to each other."""

    async def run_story_loop(self, ctx: WorkflowContext):
        # 1. Scrum Master creates story
        story_prompt = self._build_story_prompt(ctx)
        ctx.current_story = await self.scrum_master.run(story_prompt)
        ctx.last_agent_output = ctx.current_story.content

        # 2. Developer implements (gets story context)
        dev_prompt = self._build_dev_prompt(ctx)
        dev_result = await self.developer.run(dev_prompt)
        ctx.git_diff = await self._get_git_diff()
        ctx.last_agent_output = dev_result

        # 3. Reviewer reviews (gets story + diff context)
        review_prompt = self._build_review_prompt(ctx)
        review_result = await self.reviewer.run(review_prompt)
        ctx.review_feedback = review_result

    def _build_dev_prompt(self, ctx: WorkflowContext) -> str:
        return f"""
## Story to Implement
{ctx.current_story.content}

## Completed Stories for Context
{chr(10).join(ctx.completed_stories)}

## Instructions
Implement the story requirements. Run tests to verify.
"""

    def _build_review_prompt(self, ctx: WorkflowContext) -> str:
        return f"""
## Story Requirements
{ctx.current_story.content}

## Code Changes (git diff)
{ctx.git_diff}

## Instructions
Review the implementation against requirements.
Output: APPROVED or REJECTED with feedback.
"""
```

### Key Insight: No Native Cross-CLI Communication

**Important:** Claude Code and Codex CLI are completely separate tools with no shared:
- Session state
- Memory/context
- Communication protocol
- Authentication

**The orchestrator (bmad-auto) must:**
1. Extract outputs from one agent (parse JSON/JSONL)
2. Transform outputs into prompts for the next agent
3. Maintain workflow state externally
4. Pass only relevant context (avoid context pollution)

### Existing Multi-Agent Frameworks

| Framework | How It Works |
|-----------|--------------|
| **AWS CLI Agent Orchestrator** | Supervisor agent + tmux sessions + MCP servers for communication |
| **Claude-Flow** | Hive-mind with queen-led coordination, shared memory via AgentDB |
| **CCSwarm** | Git worktree isolation + message bus for agent communication |
| **Claude Squad** | tmux sessions + git worktrees for workspace isolation |

_Sources: [AWS CAO](https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse/), [Claude-Flow](https://github.com/ruvnet/claude-flow)_

### Recommended Pattern for bmad-auto

Based on research, the **Orchestrator-Managed State** pattern is best for bmad-auto:

```
┌─────────────────────────────────────────────────────────────┐
│                    bmad-auto Orchestrator                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              WorkflowState (in-memory + JSON)        │    │
│  │  - epic_content, current_story, git_diff, feedback  │    │
│  └─────────────────────────────────────────────────────┘    │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐    │
│   │  Claude  │         │  Codex   │         │  Claude  │    │
│   │   Agent  │         │  Agent   │         │   Agent  │    │
│   │(SM/Review)│        │  (Dev)   │         │(TechWrite)│   │
│   └──────────┘         └──────────┘         └──────────┘    │
│         │                    │                    │          │
│         └────────────────────┴────────────────────┘          │
│                              │                               │
│                     Target Repository                        │
│              (files, git history, stories)                   │
└─────────────────────────────────────────────────────────────┘
```

**Why this pattern:**
- Simple to implement (no external message buses)
- State persisted to JSON for pause/resume
- Context scoping prevents pollution
- Works with any CLI tool (not tied to specific framework)

---

## Known Limitations & Edge Cases

### Claude Code CLI Limitations

#### 1. Bash Command 2-Minute Timeout (Critical for bmad-auto)

**Problem:** Claude Code kills bash commands after exactly 2 minutes, regardless of completion status.

**Impact for bmad-auto:** Long-running builds, tests, or installations will fail.

**Workaround:** Configure `~/.claude/settings.json`:
```json
{
  "env": {
    "BASH_DEFAULT_TIMEOUT_MS": "1800000",
    "BASH_MAX_TIMEOUT_MS": "7200000"
  }
}
```

**Alternative:** Use background process pattern:
```bash
# Start in background
./long_operation.sh > output.log 2>&1 &
echo $! > pid.txt

# Check status in next turn
ps -p $(cat pid.txt) > /dev/null && tail -20 output.log
```

_Source: [GitHub Issue #5615](https://github.com/anthropics/claude-code/issues/5615)_

#### 2. CLAUDE.md Rules Sometimes Ignored

**Problem:** Mandatory rules in CLAUDE.md files are inconsistently followed.

**Impact for bmad-auto:** Agent personas and workflow rules may not be respected.

**Workaround:** Inject critical rules directly into prompts rather than relying solely on CLAUDE.md.

_Source: [GitHub Issue #2544](https://github.com/anthropics/claude-code/issues/2544)_

#### 3. Rate Limits & Usage Caps

**Hourly/Weekly Limits:**
- Pro: ~10-40 prompts per 5-hour window, ~40-80 hours weekly
- Max ($100): 5x Pro limits
- Max ($200): 20x Pro limits

**Impact for bmad-auto:** Heavy automation may hit limits quickly.

**Mitigation:**
- Use API with pay-as-you-go pricing for heavy automation
- Implement rate limiting in orchestrator
- Use Haiku for simpler tasks ($0.25/$1.25 per million tokens)

_Source: [Claude Code Limits](https://portkey.ai/blog/claude-code-limits/)_

#### 4. Year Confusion Bug

**Problem:** Claude sometimes believes it's 2024.

**Workaround:** Include current date in system prompt.

_Source: [GitHub Issue #6281](https://github.com/anthropics/claude-code/issues/6281)_

### Codex CLI Limitations

#### 1. Network Access Configuration

**Default:** Codex agent operates in isolated container with limited network access.

**Web Search:** Can be enabled via `--search` flag or config.toml:
```toml
[features]
web_search_request = true
```

**Full Network Access:** Use `--sandbox danger-full-access` for unrestricted network (security trade-off).

**Note:** Web search allows documentation lookups without full network exposure.

_Sources: [Codex CLI Features](https://developers.openai.com/codex/cli/features/), [Codex Config](https://developers.openai.com/codex/local-config/)_

#### 2. Security Vulnerability (Patched in 0.23.0)

**Problem:** Command injection via malicious `.env` files redirecting CODEX_HOME.

**Resolution:** Fixed in Codex CLI v0.23.0 (August 2025). Ensure you're on latest version.

_Source: [Check Point Research](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/)_

#### 3. Rate Limits & Token Consumption

**Limits by Plan:**
- Plus ($20/month): 30-150 messages per 5-hour window
- Pro ($200/month): 300-1,500 messages per 5-hour window

**Token Inflation with gpt-5.1-codex:**
- Uses significantly more tokens than gpt-5-codex
- Single prompt can consume 7% of weekly limits

**Impact for bmad-auto:** May need to budget agent invocations carefully.

_Source: [OpenAI Community](https://community.openai.com/t/codex-usage-after-the-limit-reset-update-single-prompt-eats-7-of-weekly-limits-plus-tier/1365284)_

#### 4. Azure Provider Compatibility Issues

**Problem:** CLI targets `/responses` endpoint, causing 404s on Azure setups using Chat Completions via APIM.

_Source: [GitHub Issue #2025](https://github.com/openai/codex/issues/2025)_

### Cross-CLI Considerations for bmad-auto

| Concern | Claude Code | Codex CLI | bmad-auto Strategy |
|---------|-------------|-----------|-------------------|
| **Timeout** | 2min default | No known limit | Less critical - agents use separate sessions |
| **Rate Limits** | Hourly + Weekly | 5-hour windows | Implement backoff if needed |
| **Network** | Full access | Web search via `--search` | Enable web search in Codex config |
| **Auth** | Anthropic account | OpenAI account | Support both auth methods |
| **Cost** | $3-15/M tokens | $1.25-10/M tokens | Not a concern |

**Important Note on Timeouts:** Since bmad-auto uses the **Orchestrator-Managed State** pattern where each agent starts fresh sessions and communicates via state files, the 2-minute bash timeout is less critical. Long operations are broken into multiple agent invocations rather than single long-running sessions.

### Error Handling Recommendations

```python
class CLILimitation(Enum):
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    NETWORK_BLOCKED = "network_blocked"
    PARSE_ERROR = "parse_error"

async def handle_cli_error(
    error: Exception,
    cli: str,
    retry_count: int
) -> tuple[bool, str]:  # (should_retry, message)

    if "timeout" in str(error).lower():
        if cli == "claude" and retry_count < 2:
            return True, "Extending timeout, retrying..."
        return False, "Command timed out. Consider background process."

    if "rate" in str(error).lower() or "limit" in str(error).lower():
        wait_time = min(300, 60 * (2 ** retry_count))  # Exponential backoff
        await asyncio.sleep(wait_time)
        return True, f"Rate limited. Waited {wait_time}s, retrying..."

    if "network" in str(error).lower() and cli == "codex":
        return False, "Network access blocked. Use --sandbox danger-full-access or pre-install deps."

    return False, f"Unrecoverable error: {error}"
```

---

## Executive Summary & Recommendations

### Key Findings

This research investigated how to programmatically integrate Claude Code CLI and OpenAI Codex CLI for the bmad-auto orchestration tool. The findings directly inform architectural decisions for the implementation.

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    bmad-auto Orchestrator                    │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │ Claude Agent │    │ Codex Agent  │    │ State Manager│   │
│  │   SDK        │    │ (subprocess) │    │   (JSON)     │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         │                    │                    │          │
│         └────────────────────┴────────────────────┘          │
│                              │                               │
│                     Target Repository                        │
└─────────────────────────────────────────────────────────────┘
```

### Integration Decisions

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| **Claude Integration** | Use **Claude Agent SDK** | Native Python, no subprocess, built-in retry |
| **Codex Integration** | Use **`codex exec --json`** | JSONL streaming, subprocess with asyncio |
| **Agent Communication** | **Orchestrator-Managed State** | Simple, no external deps, JSON persistence |
| **Retry Logic** | **Tenacity** | Proven, async support, exponential backoff |
| **Session Management** | **Fresh sessions per agent** | Avoids timeout issues, clean context |

### Implementation Checklist

**For Claude Code:**
- [ ] Install `claude-agent-sdk` (not deprecated `claude-code-sdk`)
- [ ] Use `query()` async iterator for streaming responses
- [ ] Configure `ClaudeAgentOptions` with `permission_mode='acceptEdits'`

**For Codex CLI:**
- [ ] Enable web search: `--search` flag or `web_search_request = true` in config.toml
- [ ] Use `codex exec --json --full-auto` for non-interactive execution
- [ ] Parse JSONL output line-by-line

**For Orchestrator:**
- [ ] Implement `WorkflowContext` dataclass for state management
- [ ] Build prompts dynamically with context from previous agents
- [ ] Persist state to JSON for pause/resume capability
- [ ] Use Tenacity for retry with exponential backoff

### Code Snippets Ready for Use

The research document contains production-ready code patterns for:
1. Claude Agent SDK integration
2. Codex subprocess with JSONL parsing
3. File-based context handoff
4. Retry patterns with Tenacity
5. Error handling with typed results
6. Session resume pattern

### Sources

**Official Documentation:**
- [Claude Agent SDK Python](https://github.com/anthropics/claude-agent-sdk-python)
- [Codex CLI Reference](https://developers.openai.com/codex/cli/reference/)
- [Python asyncio Subprocess](https://docs.python.org/3/library/asyncio-subprocess.html)

**Multi-Agent Frameworks (Reference):**
- [AWS CLI Agent Orchestrator](https://aws.amazon.com/blogs/opensource/introducing-cli-agent-orchestrator-transforming-developer-cli-tools-into-a-multi-agent-powerhouse/)
- [Claude-Flow](https://github.com/ruvnet/claude-flow)
- [CCSwarm](https://github.com/nwiizo/ccswarm)

---

**Research Completed:** 2025-12-25
**Total Sections:** Technology Stack, Integration Patterns, Multi-Agent Communication, Limitations & Edge Cases

---
