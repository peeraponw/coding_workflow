# Non-Functional Requirements

## Reliability

- NFR1: State file must be written atomically to prevent corruption during unexpected termination
- NFR2: Resume operation must restore exact workflow position 100% of the time when state file is intact
- NFR3: System must detect and report corrupted state files rather than proceeding with partial data
- NFR4: Git operations must be atomic—no partial commits that leave repository in inconsistent state
- NFR5: Agent failures must not corrupt previously completed work (committed stories remain committed)

## Integration

- NFR6: System must work with Claude Agent SDK using logged-in Anthropic subscription
- NFR7: System must support GLM routing via standard ANTHROPIC_BASE_URL mechanism
- NFR8: System must parse BMAD epic files in standard markdown format
- NFR9: System must produce YAML files readable by standard YAML parsers
- NFR10: System must integrate with git CLI for branch and commit operations
- NFR11: System must work with standard YAML parsers for configuration

## Security

- NFR12: GLM credentials (ANTHROPIC_API_KEY) must only be read from environment variables, never stored in config files
- NFR13: State files must not contain API credentials or secrets
- NFR14: Log output must not expose API credentials or sensitive request/response content

