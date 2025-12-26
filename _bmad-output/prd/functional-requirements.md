# Functional Requirements

## Workflow Execution

- FR1: User can execute a story loop for an entire epic with a single command
- FR2: User can specify the epic file path as a command argument
- FR3: System can parse BMAD epic files to extract story requirements
- FR4: System can execute stories sequentially until all are complete or a failure occurs

## Agent Orchestration

- FR5: System can invoke Scrum Master agent to create user stories from epic requirements
- FR6: System can invoke Developer agent to implement story requirements
- FR7: System can invoke Reviewer agent to validate implemented code
- FR8: System can iterate the Dev → Review loop until the Reviewer approves
- FR9: System can route SM and Reviewer agents to Claude (logged-in subscription)
- FR10: System can route Developer agent to GLM via ANTHROPIC_BASE_URL
- FR11: System can pass context between agents via YAML handoff files

## State Management

- FR12: System can persist workflow state to YAML file after each phase completion
- FR13: User can resume an interrupted workflow from the exact point of interruption
- FR14: System can detect incomplete workflow state on startup
- FR15: System can recover gracefully from rate limit errors by pausing and persisting state
- FR16: System can recover gracefully from API errors by pausing and persisting state

## Progress Monitoring

- FR17: User can check current workflow status without interrupting execution
- FR18: System can display current agent, action, and phase in progress
- FR19: System can display completed stories with commit references
- FR20: System can log workflow progression with timestamps to terminal
- FR21: System can log handoff events showing source agent, target agent, and reason

## Git Integration

- FR22: System can create a feature branch for the epic automatically
- FR23: System can commit code after each story passes review
- FR24: System can include story reference in commit message
- FR25: User can configure branch naming prefix

## Configuration

- FR26: User can configure agent model assignments in .bmad-auto.yaml
- FR27: System can read GLM credentials from ANTHROPIC_API_KEY environment variable
- FR28: System can read GLM endpoint from ANTHROPIC_BASE_URL environment variable
- FR29: User can configure default epic path in config file
- FR30: User can configure state file location in config file
- FR31: User can configure git auto-branch and auto-commit behavior

## Error Handling

- FR32: System can report clear error messages indicating failure reason and location
- FR33: System can exit with distinct exit codes for success, error, paused, and config error states
- FR34: System can preserve state integrity during unexpected failures
