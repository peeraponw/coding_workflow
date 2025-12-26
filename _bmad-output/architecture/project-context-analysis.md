# Project Context Analysis

## Requirements Overview

**Functional Requirements:**
34 requirements across 6 domains:
- **Workflow Execution (FR1-4):** Epic parsing, sequential story execution, single-command invocation
- **Agent Orchestration (FR5-11):** SM/Dev/Reviewer agent coordination, hierarchical model routing (Claude for SM/Reviewer, GLM for Dev), YAML handoff files
- **State Management (FR12-16):** YAML persistence, exact-point resume, graceful error recovery
- **Progress Monitoring (FR17-21):** Non-blocking status, timestamped logging, handoff event visibility
- **Git Integration (FR22-25):** Auto-branch creation, auto-commit with story references
- **Configuration & Error Handling (FR26-34):** YAML config, env var credentials, distinct exit codes

**Non-Functional Requirements:**
14 requirements across 3 domains:
- **Reliability (NFR1-5):** Atomic state writes, 100% resume reliability, corruption detection, atomic git ops
- **Integration (NFR6-11):** Claude Agent SDK, GLM via ANTHROPIC_BASE_URL, standard YAML parser, git CLI
- **Security (NFR12-14):** Credentials from env vars only, no secrets in state files or logs

**Scale & Complexity:**

- Primary domain: Python CLI / Developer Tooling
- Complexity level: Low (greenfield, single developer, no regulated domain)
- Estimated architectural components: ~5-7 (CLI parser, orchestrator, agent adapters, state manager, git handler, config loader, logger)

## Technical Constraints & Dependencies

- **Claude Agent SDK** required for Claude-based agents (SM, Reviewer)
- **GLM routing** via ANTHROPIC_BASE_URL for cost-efficient Dev agent
- **YAML format** for state persistence, inter-agent handoff, and user configuration (consistency over convention)
- **Git CLI** for branch/commit operations (not library-based)
- **uvx distribution** requires proper entry point and packaging

## Cross-Cutting Concerns Identified

1. **State Integrity:** Every phase must persist state atomically before proceeding
2. **Error Recovery:** Graceful pause on failure with clear messaging and resumable state
3. **Context Management:** Orchestrator must inject appropriate context without pollution
4. **Logging:** Structured, timestamped logs with handoff visibility for debugging
5. **Security Boundaries:** Credential isolation from state and logs
